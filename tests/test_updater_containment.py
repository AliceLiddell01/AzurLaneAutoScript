import importlib
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from deploy.config import (
    ConfigModel,
    DeployConfig,
    FORK_REPOSITORY,
    normalize_known_repository,
)
from deploy.git import GitManager, UpdateGuardResult
from deploy.utils import poor_yaml_read


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEPLOY_DEFAULTS = (
    REPOSITORY_ROOT / "deploy" / "template",
    REPOSITORY_ROOT / "config" / "deploy.template.yaml",
    REPOSITORY_ROOT / "config" / "deploy.template-linux.yaml",
    REPOSITORY_ROOT / "config" / "deploy.template-docker.yaml",
    REPOSITORY_ROOT / "config" / "deploy.template-AidLux.yaml",
)


class DeployDefaultsTests(unittest.TestCase):
    def test_all_active_deploy_templates_use_contained_defaults(self):
        expected = {
            "Repository": FORK_REPOSITORY,
            "AutoUpdate": False,
            "CheckUpdateInterval": 0,
            "AutoRestartTime": None,
        }
        for path in DEPLOY_DEFAULTS:
            with self.subTest(path=path):
                data = poor_yaml_read(str(path))
                for key, value in expected.items():
                    self.assertEqual(data[key], value)

        self.assertEqual(ConfigModel.Repository, FORK_REPOSITORY)
        self.assertFalse(ConfigModel.AutoUpdate)
        self.assertEqual(ConfigModel.CheckUpdateInterval, 0)
        self.assertIsNone(ConfigModel.AutoRestartTime)

    def test_known_repository_forms_normalize_to_fork(self):
        legacy = (
            "global",
            "https://github.com/LmeSzinc/AzurLaneAutoScript",
            "https://github.com/LmeSzinc/AzurLaneAutoScript.git",
            "https://github.com/LmeSzinc/AzurLaneAutoScript/",
            "https://github.com/LmeSzinc/AzurLaneAutoScript.git/",
        )
        for repository in legacy:
            with self.subTest(repository=repository):
                self.assertEqual(normalize_known_repository(repository), FORK_REPOSITORY)

    def test_legacy_migration_is_persisted_disabled_and_idempotent(self):
        for repository in (
            "global",
            "https://github.com/LmeSzinc/AzurLaneAutoScript",
            "https://github.com/LmeSzinc/AzurLaneAutoScript.git/",
        ):
            with self.subTest(repository=repository), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "deploy.yaml"
                path.write_text(
                    "\n".join(
                        (
                            "Deploy:",
                            "  Git:",
                            f"    Repository: {repository}",
                            "    AutoUpdate: true",
                            "  Webui:",
                            "    WebuiPort: 32100",
                            "",
                        )
                    ),
                    encoding="utf-8",
                )

                first = DeployConfig(file=str(path))
                second = DeployConfig(file=str(path))
                persisted = poor_yaml_read(str(path))

                self.assertEqual(first.Repository, FORK_REPOSITORY)
                self.assertFalse(first.AutoUpdate)
                self.assertEqual(second.Repository, FORK_REPOSITORY)
                self.assertFalse(second.AutoUpdate)
                self.assertEqual(persisted["Repository"], FORK_REPOSITORY)
                self.assertFalse(persisted["AutoUpdate"])
                self.assertEqual(persisted["WebuiPort"], 32100)

    def test_custom_repository_is_preserved_but_not_approved(self):
        custom = "https://example.invalid/owner/custom"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "deploy.yaml"
            path.write_text(
                "\n".join(
                    (
                        "Deploy:",
                        "  Git:",
                        f"    Repository: {custom}",
                        "    AutoUpdate: true",
                        "",
                    )
                ),
                encoding="utf-8",
            )
            config = DeployConfig(file=str(path))
            persisted = poor_yaml_read(str(path))

        self.assertEqual(config.Repository, custom)
        self.assertEqual(persisted["Repository"], custom)


class UpdateGuardTests(unittest.TestCase):
    @staticmethod
    def manager(repository=FORK_REPOSITORY, auto_update=True, status=""):
        manager = object.__new__(GitManager)
        manager.AutoUpdate = auto_update
        manager.Repository = repository
        manager.Branch = "master"
        manager.root_filepath = str(REPOSITORY_ROOT)
        manager.git = "git"
        outputs = {
            ("rev-parse", "--is-inside-work-tree"): "true",
            ("symbolic-ref", "--quiet", "--short", "HEAD"): "master",
            ("status", "--porcelain", "--untracked-files=normal"): status,
            ("remote", "get-url", "origin"): FORK_REPOSITORY,
            ("rev-parse", "--verify", "--quiet", "origin/master"): "a" * 40,
            ("rev-parse", "--git-path", "index.lock"): ".git/index.lock",
            ("rev-parse", "--git-path", "HEAD.lock"): ".git/HEAD.lock",
            ("rev-parse", "--git-path", "refs/heads/master.lock"): (
                ".git/refs/heads/master.lock"
            ),
        }
        manager._git_output = mock.Mock(side_effect=lambda *args: outputs.get(args))
        manager._git_success = mock.Mock(return_value=True)
        return manager

    def test_disabled_updater_denies_before_git_inspection(self):
        manager = self.manager(auto_update=False)
        result = manager.updater_guard("check")
        self.assertFalse(result)
        self.assertIn("disabled", result.reason)
        manager._git_output.assert_not_called()

    def test_wrong_or_regional_repository_denies_before_git_inspection(self):
        for repository in ("https://example.invalid/custom", "cn", "jp", "tw"):
            with self.subTest(repository=repository):
                manager = self.manager(repository=repository)
                result = manager.updater_guard("update")
                self.assertFalse(result)
                manager._git_output.assert_not_called()

    def test_dirty_checkout_is_denied(self):
        manager = self.manager(status=" M tracked.txt\n?? untracked.txt")
        result = manager.updater_guard("update")
        self.assertFalse(result)
        self.assertIn("local changes", result.reason)

    def test_mismatched_branch_or_remote_is_denied(self):
        manager = self.manager()
        manager._git_output.side_effect = lambda *args: {
            ("rev-parse", "--is-inside-work-tree"): "true",
            ("symbolic-ref", "--quiet", "--short", "HEAD"): "feature",
        }.get(args)
        result = manager.updater_guard("update")
        self.assertFalse(result)
        self.assertIn("does not match", result.reason)

        manager = self.manager()
        original = manager._git_output.side_effect
        manager._git_output.side_effect = lambda *args: (
            "https://example.invalid/other"
            if args == ("remote", "get-url", "origin")
            else original(*args)
        )
        result = manager.updater_guard("update")
        self.assertFalse(result)
        self.assertIn("origin remote", result.reason)

    def test_lock_file_is_denied_without_removal(self):
        manager = self.manager()
        with mock.patch("deploy.git.os.path.exists", return_value=True):
            result = manager.updater_guard("update")
        self.assertFalse(result)
        self.assertIn("will not be removed", result.reason)

    def test_diverged_checkout_is_denied(self):
        manager = self.manager()
        manager._git_success.return_value = False
        result = manager.updater_guard("update")
        self.assertFalse(result)
        self.assertIn("diverged", result.reason)

    def test_clean_fork_checkout_is_allowed(self):
        manager = self.manager()
        result = manager.updater_guard("update")
        self.assertTrue(result)
        self.assertIn(FORK_REPOSITORY, result.reason)


class DisposableGitUpdateTests(unittest.TestCase):
    @staticmethod
    def git(*args, cwd=None):
        return subprocess.run(
            ["git"] + list(args),
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.remote = root / "remote.git"
        self.seed = root / "seed"
        self.checkout = root / "checkout"

        self.git("init", "--bare", "--initial-branch=master", str(self.remote))
        self.git("init", "--initial-branch=master", str(self.seed))
        self.git("config", "user.email", "tests@example.invalid", cwd=self.seed)
        self.git("config", "user.name", "Updater tests", cwd=self.seed)
        (self.seed / "tracked.txt").write_text("original\n", encoding="utf-8")
        self.git("add", "tracked.txt", cwd=self.seed)
        self.git("commit", "-m", "initial", cwd=self.seed)
        self.git("remote", "add", "origin", str(self.remote), cwd=self.seed)
        self.git("push", "-u", "origin", "master", cwd=self.seed)
        self.git("clone", str(self.remote), str(self.checkout))
        self.git("config", "user.email", "tests@example.invalid", cwd=self.checkout)
        self.git("config", "user.name", "Updater tests", cwd=self.checkout)

        self.manager = object.__new__(GitManager)
        self.manager.AutoUpdate = True
        self.manager.Repository = FORK_REPOSITORY
        self.manager.Branch = "master"
        self.manager.root_filepath = str(self.checkout)
        self.manager.git = "git"

    def tearDown(self):
        self.tmp.cleanup()

    def fork_policy(self, repository):
        return repository in {FORK_REPOSITORY, str(self.remote)}

    def test_dirty_files_survive_and_remote_is_not_mutated(self):
        tracked = self.checkout / "tracked.txt"
        untracked = self.checkout / "untracked.txt"
        tracked.write_text("local edit\n", encoding="utf-8")
        untracked.write_text("keep me\n", encoding="utf-8")
        before_remote = self.git(
            "remote", "get-url", "origin", cwd=self.checkout
        ).stdout.strip()

        with mock.patch("deploy.git.is_fork_repository", side_effect=self.fork_policy):
            result = self.manager.git_install()

        self.assertEqual(result, GitManager.UPDATE_BLOCKED)
        self.assertEqual(tracked.read_text(encoding="utf-8"), "local edit\n")
        self.assertEqual(untracked.read_text(encoding="utf-8"), "keep me\n")
        after_remote = self.git(
            "remote", "get-url", "origin", cwd=self.checkout
        ).stdout.strip()
        self.assertEqual(after_remote, before_remote)

    def test_clean_checkout_applies_only_fast_forward(self):
        (self.seed / "remote.txt").write_text("remote update\n", encoding="utf-8")
        self.git("add", "remote.txt", cwd=self.seed)
        self.git("commit", "-m", "remote update", cwd=self.seed)
        self.git("push", "origin", "master", cwd=self.seed)
        before_remote = self.git(
            "remote", "get-url", "origin", cwd=self.checkout
        ).stdout.strip()

        with mock.patch("deploy.git.is_fork_repository", side_effect=self.fork_policy):
            result = self.manager.git_install()

        self.assertEqual(result, GitManager.UPDATE_APPLIED)
        self.assertEqual(
            (self.checkout / "remote.txt").read_text(encoding="utf-8"),
            "remote update\n",
        )
        self.assertEqual(
            self.git("remote", "get-url", "origin", cwd=self.checkout).stdout.strip(),
            before_remote,
        )

    def test_diverged_checkout_aborts_without_changing_head(self):
        (self.checkout / "local.txt").write_text("local\n", encoding="utf-8")
        self.git("add", "local.txt", cwd=self.checkout)
        self.git("commit", "-m", "local commit", cwd=self.checkout)

        (self.seed / "remote.txt").write_text("remote\n", encoding="utf-8")
        self.git("add", "remote.txt", cwd=self.seed)
        self.git("commit", "-m", "remote commit", cwd=self.seed)
        self.git("push", "origin", "master", cwd=self.seed)
        self.git("fetch", "origin", "master", cwd=self.checkout)
        before = self.git("rev-parse", "HEAD", cwd=self.checkout).stdout.strip()

        with mock.patch("deploy.git.is_fork_repository", side_effect=self.fork_policy):
            result = self.manager.git_install()

        self.assertEqual(result, GitManager.UPDATE_BLOCKED)
        after = self.git("rev-parse", "HEAD", cwd=self.checkout).stdout.strip()
        self.assertEqual(after, before)
        self.assertTrue((self.checkout / "local.txt").exists())


class WebUpdaterContainmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.import_tmp = tempfile.TemporaryDirectory()
        root = Path(cls.import_tmp.name)
        (root / "deploy").mkdir()
        (root / "config").mkdir()
        shutil.copyfile(
            REPOSITORY_ROOT / "deploy" / "template",
            root / "deploy" / "template",
        )

        fake_modules = {}
        for name in ("module", "module.base", "module.webui"):
            package = types.ModuleType(name)
            package.__path__ = []
            fake_modules[name] = package

        retry_module = types.ModuleType("module.base.retry")
        retry_module.retry = lambda *args, **kwargs: (lambda function: function)
        fake_modules["module.base.retry"] = retry_module

        logger_module = types.ModuleType("module.logger")
        logger_module.logger = mock.Mock()
        fake_modules["module.logger"] = logger_module

        config_module = types.ModuleType("module.webui.config")

        class WebDeployConfig(DeployConfig):
            def show_config(self):
                pass

        config_module.DeployConfig = WebDeployConfig
        fake_modules["module.webui.config"] = config_module

        process_module = types.ModuleType("module.webui.process_manager")

        class ProcessManager:
            @staticmethod
            def running_instances():
                return []

        process_module.ProcessManager = ProcessManager
        fake_modules["module.webui.process_manager"] = process_module

        setting_module = types.ModuleType("module.webui.setting")
        setting_module.State = type(
            "State",
            (),
            {"deploy_config": None, "restart_event": None},
        )
        fake_modules["module.webui.setting"] = setting_module

        utils_module = types.ModuleType("module.webui.utils")
        utils_module.TaskHandler = type("TaskHandler", (), {})
        utils_module.get_next_time = lambda value: value
        fake_modules["module.webui.utils"] = utils_module

        previous = Path.cwd()
        try:
            os.chdir(root)
            updater_path = (
                REPOSITORY_ROOT / "module" / "webui" / "updater.py"
            )
            spec = importlib.util.spec_from_file_location(
                "contained_webui_updater",
                updater_path,
            )
            cls.updater_module = importlib.util.module_from_spec(spec)
            with mock.patch.dict(sys.modules, fake_modules):
                spec.loader.exec_module(cls.updater_module)
        finally:
            os.chdir(previous)

    @classmethod
    def tearDownClass(cls):
        cls.import_tmp.cleanup()

    def updater(self):
        updater = object.__new__(self.updater_module.Updater)
        updater.state = 0
        return updater

    def test_disabled_update_calls_no_git_or_pip(self):
        updater = self.updater()
        updater.updater_guard = mock.Mock(
            return_value=UpdateGuardResult(False, "automatic updates are disabled")
        )
        updater.git_install = mock.Mock()
        updater.pip_install = mock.Mock()

        self.assertFalse(updater.update())
        self.assertEqual(updater.state, "disabled")
        updater.git_install.assert_not_called()
        updater.pip_install.assert_not_called()

    def test_direct_pip_entry_is_guarded(self):
        updater = self.updater()
        updater.updater_guard = mock.Mock(
            return_value=UpdateGuardResult(False, "automatic updates are disabled")
        )
        with mock.patch.object(
            self.updater_module.PipManager,
            "pip_install",
        ) as pip_install:
            self.assertFalse(updater.pip_install())
        self.assertEqual(updater.state, "disabled")
        pip_install.assert_not_called()

    def test_no_update_does_not_run_pip(self):
        updater = self.updater()
        updater.updater_guard = mock.Mock(
            return_value=UpdateGuardResult(True, "allowed")
        )
        updater.git_install = mock.Mock(return_value=GitManager.UPDATE_CURRENT)
        updater.pip_install = mock.Mock()

        self.assertFalse(updater.update())
        updater.pip_install.assert_not_called()

    def test_applied_fast_forward_may_run_pip(self):
        updater = self.updater()
        updater.updater_guard = mock.Mock(
            return_value=UpdateGuardResult(True, "allowed")
        )
        updater.git_install = mock.Mock(return_value=GitManager.UPDATE_APPLIED)
        updater.pip_install = mock.Mock()

        self.assertTrue(updater.update())
        updater.pip_install.assert_called_once_with()

    def test_denied_manual_update_does_not_inspect_processes(self):
        updater = self.updater()
        updater.updater_guard = mock.Mock(
            return_value=UpdateGuardResult(False, "wrong repository")
        )
        with mock.patch.object(
            self.updater_module.ProcessManager, "running_instances"
        ) as running_instances:
            self.assertFalse(updater.run_update())
        running_instances.assert_not_called()


class ActiveUpdaterInvariantTests(unittest.TestCase):
    def test_manual_scheduled_and_direct_paths_share_guarded_contract(self):
        updater_source = (
            REPOSITORY_ROOT / "module" / "webui" / "updater.py"
        ).read_text(encoding="utf-8")
        self.assertIn('self.updater_guard("update")', updater_source)
        self.assertIn("status = self.check_update_status()", updater_source)
        self.assertIn("self.check_update()", updater_source)
        self.assertIn("self.run_update()", updater_source)

    def test_active_updater_paths_have_no_destructive_or_cdn_fallback(self):
        active_paths = (
            REPOSITORY_ROOT / "deploy" / "git.py",
            REPOSITORY_ROOT / "module" / "webui" / "updater.py",
        )
        forbidden = (
            "reset --hard",
            "remote set-url",
            "git clean",
            "checkout --force",
            "LmeSzinc_AzurLaneAutoScript_master",
            "GitOverCdnClient",
            "goc_client",
        )
        for path in active_paths:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                for value in forbidden:
                    self.assertNotIn(value, text)

    def test_direct_module_blocks_do_not_run_updater(self):
        for path in (
            REPOSITORY_ROOT / "deploy" / "git.py",
            REPOSITORY_ROOT / "module" / "webui" / "updater.py",
        ):
            text = path.read_text(encoding="utf-8")
            main_block = text.split('if __name__ == "__main__":', 1)[1]
            with self.subTest(path=path):
                self.assertNotIn(".update()", main_block)
                self.assertNotIn(".get_status()", main_block)


if __name__ == "__main__":
    unittest.main()
