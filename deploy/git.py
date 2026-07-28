import os
import subprocess

from deploy.config import (
    DeployConfig,
    FORK_REPOSITORY,
    UNSUPPORTED_REPOSITORY_ALIASES,
    is_fork_repository,
)
from deploy.logger import logger
from deploy.utils import cached_property


class UpdateGuardResult:
    def __init__(self, allowed, reason):
        self.allowed = allowed
        self.reason = reason

    def __bool__(self):
        return self.allowed

    def __repr__(self):
        return f"UpdateGuardResult(allowed={self.allowed!r}, reason={self.reason!r})"


class GitManager(DeployConfig):
    UPDATE_BLOCKED = "blocked"
    UPDATE_CURRENT = "current"
    UPDATE_AVAILABLE = "available"
    UPDATE_APPLIED = "applied"
    UPDATE_FAILED = "failed"

    @cached_property
    def git(self):
        exe = self.filepath("GitExecutable")
        if os.path.exists(exe):
            return exe

        logger.warning(f"GitExecutable: {exe} does not exist, use `git` instead")
        return "git"

    def _run_git(self, *args):
        command = [self.git] + list(args)
        logger.info(f"Execute: {command}")
        try:
            return subprocess.run(
                command,
                cwd=self.root_filepath,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=False,
                timeout=300,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            logger.warning(f"Git command failed: {exc}")
            return None

    def _git_output(self, *args):
        result = self._run_git(*args)
        if result is None or result.returncode != 0:
            return None
        return result.stdout.strip()

    def _git_success(self, *args):
        result = self._run_git(*args)
        return result is not None and result.returncode == 0

    def _deny_update(self, reason):
        logger.warning(f"Updater containment blocked operation: {reason}")
        return UpdateGuardResult(False, reason)

    def updater_guard(self, operation):
        """
        Decide whether an updater entry point may perform any network, Git,
        dependency, process-management, or reload operation.
        """
        if operation not in {"check", "update"}:
            return self._deny_update(f"unsupported operation '{operation}'")
        if not self.AutoUpdate:
            return self._deny_update("automatic updates are disabled")

        repository = self.Repository
        if not is_fork_repository(repository):
            if (
                isinstance(repository, str)
                and repository.strip().lower() in UNSUPPORTED_REPOSITORY_ALIASES
            ):
                return self._deny_update(
                    f"repository alias '{repository}' is unsupported by the EN-only fork"
                )
            return self._deny_update("repository target is not the approved fork")

        if self._git_output("rev-parse", "--is-inside-work-tree") != "true":
            return self._deny_update("checkout is not a Git working tree")

        branch = self._git_output("symbolic-ref", "--quiet", "--short", "HEAD")
        if branch != self.Branch:
            return self._deny_update(
                f"checkout branch {branch!r} does not match configured branch {self.Branch!r}"
            )

        status = self._git_output("status", "--porcelain", "--untracked-files=normal")
        if status is None:
            return self._deny_update("unable to inspect checkout status")
        if status:
            return self._deny_update("checkout has tracked or untracked local changes")

        remote = self._git_output("remote", "get-url", "origin")
        if remote is None:
            return self._deny_update("origin remote is missing")
        if not is_fork_repository(remote):
            return self._deny_update("origin remote is not the approved fork")

        remote_ref = f"origin/{self.Branch}"
        if self._git_output("rev-parse", "--verify", "--quiet", remote_ref) is None:
            return self._deny_update(f"remote-tracking ref {remote_ref!r} is missing")
        if not self._git_success("merge-base", "--is-ancestor", "HEAD", remote_ref):
            return self._deny_update(
                f"checkout is ahead of or diverged from {remote_ref!r}"
            )

        for lock_name in (
            "index.lock",
            "HEAD.lock",
            f"refs/heads/{self.Branch}.lock",
        ):
            lock_path = self._git_output("rev-parse", "--git-path", lock_name)
            if lock_path:
                if not os.path.isabs(lock_path):
                    lock_path = os.path.join(self.root_filepath, lock_path)
                if os.path.exists(lock_path):
                    return self._deny_update(
                        f"Git lock file exists and will not be removed: {lock_name}"
                    )

        return UpdateGuardResult(
            True,
            f"{operation} is allowed for {FORK_REPOSITORY} on {self.Branch}",
        )

    def check_update_status(self, operation="check"):
        guard = self.updater_guard(operation)
        if not guard:
            return self.UPDATE_BLOCKED

        source = "origin"
        result = self._run_git("fetch", "--no-tags", source, self.Branch)
        if result is None or result.returncode != 0:
            logger.warning("Git fetch failed")
            return self.UPDATE_FAILED

        guard = self.updater_guard(operation)
        if not guard:
            return self.UPDATE_BLOCKED

        local = self._git_output("rev-parse", "HEAD")
        remote = self._git_output("rev-parse", f"{source}/{self.Branch}")
        if not local or not remote:
            logger.warning("Unable to resolve local or remote revision")
            return self.UPDATE_FAILED
        if local == remote:
            logger.info("No update")
            return self.UPDATE_CURRENT

        logger.info(f"New update available: {remote[:8]}")
        return self.UPDATE_AVAILABLE

    def git_install(self):
        logger.hr("Update Alas", 0)
        status = self.check_update_status(operation="update")
        if status != self.UPDATE_AVAILABLE:
            return status

        remote_ref = f"origin/{self.Branch}"
        result = self._run_git("merge", "--ff-only", remote_ref)
        if result is None or result.returncode != 0:
            logger.warning("Fast-forward update failed; checkout was not reset")
            return self.UPDATE_FAILED

        logger.info("Fast-forward update applied")
        return self.UPDATE_APPLIED


if __name__ == "__main__":
    logger.warning("Direct updater execution is disabled; no network request was made")
