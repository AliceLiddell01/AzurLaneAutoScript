import copy
from typing import Optional, Union

from deploy.logger import logger
from deploy.utils import *

FORK_REPOSITORY = "https://github.com/AliceLiddell01/AzurLaneAutoScript"
UPSTREAM_REPOSITORY = "https://github.com/LmeSzinc/AzurLaneAutoScript"
UNSUPPORTED_REPOSITORY_ALIASES = {"cn", "jp", "tw"}


def repository_identity(repository):
    """
    Return a stable GitHub repository identity without rewriting custom targets.
    """
    if not isinstance(repository, str):
        return ""

    value = repository.strip().rstrip("/")
    if value.lower().endswith(".git"):
        value = value[:-4]

    lowered = value.lower()
    if lowered.startswith("https://github.com/"):
        return lowered[len("https://"):]
    if lowered.startswith("git@github.com:"):
        return "github.com/" + lowered[len("git@github.com:"):]
    return lowered


def normalize_known_repository(repository):
    """
    Canonicalize only fork-owned and explicitly supported legacy values.
    """
    if not isinstance(repository, str):
        return repository

    value = repository.strip()
    if value.lower() == "global":
        return FORK_REPOSITORY

    identity = repository_identity(value)
    if identity in {
        repository_identity(FORK_REPOSITORY),
        repository_identity(UPSTREAM_REPOSITORY),
    }:
        return FORK_REPOSITORY
    return repository


def is_legacy_repository(repository):
    if not isinstance(repository, str):
        return False
    return (
        repository.strip().lower() == "global"
        or repository_identity(repository) == repository_identity(UPSTREAM_REPOSITORY)
    )


def is_fork_repository(repository):
    return repository_identity(repository) == repository_identity(FORK_REPOSITORY)


class ExecutionError(Exception):
    pass


class ConfigModel:
    # Git
    Repository: str = FORK_REPOSITORY
    Branch: str = "master"
    GitExecutable: str = "./toolkit/Git/mingw64/bin/git.exe"
    GitProxy: Optional[str] = None
    SSLVerify: bool = False
    AutoUpdate: bool = False

    # Python
    PythonExecutable: str = "./toolkit/python.exe"
    PypiMirror: Optional[str] = None
    InstallDependencies: bool = True
    RequirementsFile: str = "requirements.txt"

    # Adb
    AdbExecutable: str = "./toolkit/Lib/site-packages/adbutils/binaries/adb.exe"
    ReplaceAdb: bool = True
    AutoConnect: bool = True
    InstallUiautomator2: bool = True

    # Ocr
    UseOcrServer: bool = False
    StartOcrServer: bool = False
    OcrServerPort: int = 22268
    OcrClientAddress: str = "127.0.0.1:22268"

    # Update
    EnableReload: bool = True
    CheckUpdateInterval: int = 0
    AutoRestartTime: Optional[str] = None

    # Misc
    DiscordRichPresence: bool = False

    # Remote Access
    EnableRemoteAccess: bool = False
    SSHUser: Optional[str] = None
    SSHServer: Optional[str] = None
    SSHExecutable: Optional[str] = None

    # Webui
    WebuiHost: str = "0.0.0.0"
    WebuiPort: int = 22267
    WebuiSSLKey: Optional[str] = None
    WebuiSSLCert: Optional[str] = None
    Language: str = "en-US"
    Theme: str = "default"
    DpiScaling: bool = True
    Password: Optional[str] = None
    CDN: Union[str, bool] = False
    Run: Optional[str] = None

    # Dynamic
    GitOverCdn: bool = False


class DeployConfig(ConfigModel):
    def __init__(self, file=DEPLOY_CONFIG):
        """
        Args:
            file (str): User deploy config.
        """
        self.file = file
        self.config = {}
        self.config_template = {}
        self.read()

        self.show_config()

    def show_config(self):
        logger.hr("Show deploy config", 1)
        for k, v in self.config.items():
            if k in ("Password", "SSHUser"):
                continue
            if self.config_template.get(k) == v:
                continue
            logger.info(f"{k}: {v}")

        logger.info(f"Rest of the configs are the same as default")

    def read(self):
        """
        Read and update deploy config, copy `self.configs` to properties.
        """
        self.config = poor_yaml_read(DEPLOY_TEMPLATE)
        self.config_template = copy.deepcopy(self.config)
        origin = poor_yaml_read(self.file)
        self.config.update(origin)

        for key, value in self.config.items():
            if hasattr(self, key):
                super().__setattr__(key, value)

        self.config_redirect()

        if self.config != origin:
            self.write()

    def write(self):
        poor_yaml_write(self.config, self.file)

    def config_redirect(self):
        """
        Redirect deploy config, must be called after each `read()`
        """

        # Bypass webui.config.DeployConfig.__setattr__()
        # Don't write these into deploy.yaml
        super().__setattr__('GitOverCdn', False)

        repository = self.Repository
        normalized = normalize_known_repository(repository)
        if normalized != repository:
            self.config['Repository'] = normalized
            super().__setattr__('Repository', normalized)

        if is_legacy_repository(repository):
            self.config['AutoUpdate'] = False
            super().__setattr__('AutoUpdate', False)
            logger.warning(
                f'Legacy update repository migrated to {FORK_REPOSITORY}; '
                f'automatic updates remain disabled'
            )
        elif isinstance(repository, str) and (
            repository.strip().lower() in UNSUPPORTED_REPOSITORY_ALIASES
        ):
            logger.error(
                f"Repository alias '{repository}' is unsupported by the EN-only fork; "
                f"updater operations will be denied"
            )

    def filepath(self, key):
        """
        Args:
            key (str):

        Returns:
            str: Absolute filepath.
        """
        return (
            os.path.abspath(os.path.join(self.root_filepath, self.config[key]))
            .replace(r"\\", "/")
            .replace("\\", "/")
            .replace('"', '"')
        )

    @cached_property
    def root_filepath(self):
        return (
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
            .replace(r"\\", "/")
            .replace("\\", "/")
            .replace('"', '"')
        )

    def execute(self, command, allow_failure=False, output=True):
        """
        Args:
            command (str):
            allow_failure (bool):
            output(bool):

        Returns:
            bool: If success.
                Terminate installation if failed to execute and not allow_failure.
        """
        command = command.replace(r"\\", "/").replace("\\", "/").replace('"', '"')
        if not output:
            command = command + ' >nul 2>nul'
        logger.info(command)
        error_code = os.system(command)
        if error_code:
            if allow_failure:
                logger.info(f"[ allowed failure ], error_code: {error_code}")
                return False
            else:
                logger.info(f"[ failure ], error_code: {error_code}")
                self.show_error(command)
                raise ExecutionError
        else:
            logger.info(f"[ success ]")
            return True

    def show_error(self, command=None):
        logger.hr("Update failed", 0)
        self.show_config()
        logger.info("")
        logger.info(f"Last command: {command}")
        logger.info(
            "Please check your deploy settings in config/deploy.yaml "
            "and re-open Alas.exe"
        )
        logger.info("Take the screenshot of entire window if you need help")
