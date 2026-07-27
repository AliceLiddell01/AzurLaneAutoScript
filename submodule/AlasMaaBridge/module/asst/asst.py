import ctypes
import json
import os
import pathlib
import platform
from typing import Union, Optional

from .utils import InstanceOptionType, JSON


class Asst:
    CallBackType = ctypes.CFUNCTYPE(
        None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)
    """
    Callback function; see my_callback for an example

    :params:
        ``param1 message``: Message type
        ``param2 details``: json string
        ``param3 arg``:     Custom argument
    """

    @staticmethod
    def load(path: Union[pathlib.Path, str], incremental_path: Optional[Union[pathlib.Path, str, list]] = None,
             user_dir: Optional[Union[pathlib.Path, str]] = None) -> bool:
        """
        Load the DLL and resources

        :params:
            ``path``:    Directory containing the DLL and resources
            ``incremental_path``:   Directory containing incremental resources
            ``user_dir``:   Directory for user data such as logs and debug images
        """

        platform_values = {
            'windows': {
                'libpath': 'MaaCore.dll',
                'environ_var': 'PATH'
            },
            'darwin': {
                'libpath': 'libMaaCore.dylib',
                'environ_var': 'DYLD_LIBRARY_PATH'
            },
            'linux': {
                'libpath': 'libMaaCore.so',
                'environ_var': 'LD_LIBRARY_PATH'
            }
        }

        platform_type = platform.system().lower()
        if platform_type == 'windows':
            lib_import_func = ctypes.WinDLL
        else:
            lib_import_func = ctypes.CDLL

        Asst.__libpath = pathlib.Path(path) / platform_values[platform_type]['libpath']
        try:
            os.environ[platform_values[platform_type]['environ_var']] += os.pathsep + str(path)
        except KeyError:
            os.environ[platform_values[platform_type]['environ_var']] = os.pathsep + str(path)
        Asst.__lib = lib_import_func(str(Asst.__libpath))
        Asst.__set_lib_properties()

        ret: bool = True
        if user_dir:
            ret &= Asst.__lib.AsstSetUserDir(str(user_dir).encode('utf-8'))

        ret &= Asst.__lib.AsstLoadResource(str(path).encode('utf-8'))
        if incremental_path:
            if isinstance(incremental_path, list):
                for i_path in incremental_path:
                    ret &= Asst.__lib.AsstLoadResource(
                        str(i_path).encode('utf-8'))
            else:
                ret &= Asst.__lib.AsstLoadResource(
                    str(incremental_path).encode('utf-8'))

        return ret

    def __init__(self, callback: CallBackType = None, arg=None):
        """
        :params:
            ``callback``:   Callback function
            ``arg``:        Custom argument
        """

        if callback:
            self.__ptr = Asst.__lib.AsstCreateEx(callback, arg)
        else:
            self.__ptr = Asst.__lib.AsstCreate()

    def __del__(self):
        Asst.__lib.AsstDestroy(self.__ptr)
        self.__ptr = None

    def set_instance_option(self, option_type: InstanceOptionType, option_value: str):
        """
        Set an additional option
        See ${MaaAssistantArknights}/src/MaaCore/Assistant.cpp#set_instance_option

        :params:
            ``externa_config``: Additional option type
            ``config_value``:   Additional option value

        :return: Whether the option was set successfully
        """
        return Asst.__lib.AsstSetInstanceOption(self.__ptr,
                                                int(option_type), option_value.encode('utf-8'))

    def connect(self, adb_path: str, address: str, config: str = 'General'):
        """
        Connect to a device

        :params:
            ``adb_path``:       Path to the adb executable
            ``address``:        ADB address and port
            ``config``:         ADB configuration; see resource/config.json

        :return: Whether the connection succeeded
        """
        return Asst.__lib.AsstConnect(self.__ptr,
                                      adb_path.encode('utf-8'), address.encode('utf-8'), config.encode('utf-8'))

    TaskId = int

    def append_task(self, type_name: str, params: JSON = {}) -> TaskId:
        """
        Append a task

        :params:
            ``type_name``:  Task type; see the integration documentation
            ``params``:     Task parameters; see the integration documentation

        :return: Task ID for use with set_task_params
        """
        return Asst.__lib.AsstAppendTask(self.__ptr, type_name.encode('utf-8'),
                                         json.dumps(params, ensure_ascii=False).encode('utf-8'))

    def set_task_params(self, task_id: TaskId, params: JSON) -> bool:
        """
        Update task parameters dynamically

        :params:
            ``task_id``:  Task ID returned by append_task
            ``params``:   Task parameters as accepted by append_task; see the integration documentation

        :return: Whether the operation succeeded
        """
        return Asst.__lib.AsstSetTaskParams(self.__ptr, task_id, json.dumps(params, ensure_ascii=False).encode('utf-8'))

    def start(self) -> bool:
        """
        Start tasks

        :return: Whether the operation succeeded
        """
        return Asst.__lib.AsstStart(self.__ptr)

    def stop(self) -> bool:
        """
        Stop and clear all tasks

        :return: Whether the operation succeeded
        """
        return Asst.__lib.AsstStop(self.__ptr)

    def running(self) -> bool:
        """
        Whether the assistant is running

        :return: Whether the assistant is running
        """
        return Asst.__lib.AsstRunning(self.__ptr)

    @staticmethod
    def log(level: str, message: str) -> None:
        """
        Write a log entry

        :params:
            ``level``:      Log-level label
            ``message``:    Log message
        """

        Asst.__lib.AsstLog(level.encode('utf-8'), message.encode('utf-8'))

    def get_version(self) -> str:
        """
        Get the DLL version

        : return: Version string
        """
        return Asst.__lib.AsstGetVersion().decode('utf-8')

    @staticmethod
    def __set_lib_properties():
        Asst.__lib.AsstSetUserDir.restype = ctypes.c_bool
        Asst.__lib.AsstSetUserDir.argtypes = (
            ctypes.c_char_p,)

        Asst.__lib.AsstLoadResource.restype = ctypes.c_bool
        Asst.__lib.AsstLoadResource.argtypes = (
            ctypes.c_char_p,)

        Asst.__lib.AsstCreate.restype = ctypes.c_void_p
        Asst.__lib.AsstCreate.argtypes = ()

        Asst.__lib.AsstCreateEx.restype = ctypes.c_void_p
        Asst.__lib.AsstCreateEx.argtypes = (
            ctypes.c_void_p, ctypes.c_void_p,)

        Asst.__lib.AsstDestroy.argtypes = (ctypes.c_void_p,)

        Asst.__lib.AsstSetInstanceOption.restype = ctypes.c_bool
        Asst.__lib.AsstSetInstanceOption.argtypes = (
            ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p,)

        Asst.__lib.AsstConnect.restype = ctypes.c_bool
        Asst.__lib.AsstConnect.argtypes = (
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p,)

        Asst.__lib.AsstAppendTask.restype = ctypes.c_int
        Asst.__lib.AsstAppendTask.argtypes = (
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p)

        Asst.__lib.AsstSetTaskParams.restype = ctypes.c_bool
        Asst.__lib.AsstSetTaskParams.argtypes = (
            ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p)

        Asst.__lib.AsstStart.restype = ctypes.c_bool
        Asst.__lib.AsstStart.argtypes = (ctypes.c_void_p,)

        Asst.__lib.AsstStop.restype = ctypes.c_bool
        Asst.__lib.AsstStop.argtypes = (ctypes.c_void_p,)

        Asst.__lib.AsstRunning.restype = ctypes.c_bool
        Asst.__lib.AsstRunning.argtypes = (ctypes.c_void_p,)

        Asst.__lib.AsstGetVersion.restype = ctypes.c_char_p

        Asst.__lib.AsstLog.restype = None
        Asst.__lib.AsstLog.argtypes = (
            ctypes.c_char_p, ctypes.c_char_p)
