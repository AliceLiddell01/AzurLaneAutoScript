from typing import Union, Dict, List, Any, Type
from enum import Enum, IntEnum, unique, auto

JSON = Union[Dict[str, Any], List[Any], int, str, float, bool, Type[None]]


class InstanceOptionType(IntEnum):
    # Touch-mode setting， "minitouch" | "maatouch" | "adb"
    touch_type = 2
    # Whether auto battle, roguelike, and SSS may deploy operators while paused， "0" | "1"
    deployment_with_pause = 3
    # Whether to use AdbLite， "0" | "1"
    adblite_enabled = 4
    kill_on_adb_exit = 5


class StaticOptionType(IntEnum):
    invalid = 0
    cpu_ocr = 1
    gpu_ocr = 2


@unique
class Message(Enum):
    """
    Callback message

    See the callback-message documentation
    """
    InternalError = 0

    InitFailed = auto()

    ConnectionInfo = auto()

    AllTasksCompleted = auto()

    AsyncCallInfo = auto()

    Destroyed = auto()

    TaskChainError = 10000

    TaskChainStart = auto()

    TaskChainCompleted = auto()

    TaskChainExtraInfo = auto()

    TaskChainStopped = auto()

    SubTaskError = 20000

    SubTaskStart = auto()

    SubTaskCompleted = auto()

    SubTaskExtraInfo = auto()

    SubTaskStopped = auto()


@unique
class Version(Enum):
    """
    Target version
    """
    Nightly = auto()

    Beta = auto()

    Stable = auto()
