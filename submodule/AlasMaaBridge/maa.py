import os
import json
import ctypes
from cached_property import cached_property

# In order for MAA submodule to exexute,
# it is necessary to load runtime before module PIL
if os.name == 'nt':
    # This DLL is the dependency for next DLL
    # Try loading to avoid mix different versions of runtime
    try:
        ctypes.WinDLL(os.path.join(os.environ['SystemRoot'], 'System32/vcruntime140_1.dll'))
    except Exception as e:
        print(e)

    # This DLL must be loaded due to conflict issues
    ctypes.WinDLL(os.path.join(os.environ['SystemRoot'], 'System32/msvcp140.dll'))

    # These DLLS are other DLLS that MAA depends on
    # Try loading to avoid mix different versions of runtime
    try:
        ctypes.WinDLL(os.path.join(os.environ['SystemRoot'], 'System32/msvcp140_1.dll'))
        ctypes.WinDLL(os.path.join(os.environ['SystemRoot'], 'System32/concrt140.dll'))
    except Exception as e:
        print(e)

from alas import AzurLaneAutoScript
from module.exception import RequestHumanTakeover
from module.logger import logger
from submodule.AlasMaaBridge.module.config.config import ArknightsConfig
from submodule.AlasMaaBridge.module.handler.handler import AssistantHandler
from submodule.AlasMaaBridge.module.logger import log_callback


class FakeDevice:
    @staticmethod
    def empty_func(*args, **kwargs):
        pass

    def __getattr__(self, item):
        return FakeDevice.empty_func


class ArknightsAutoScript(AzurLaneAutoScript):
    @cached_property
    def device(self):
        return FakeDevice()

    @cached_property
    def config(self):
        try:
            config = ArknightsConfig(config_name=self.config_name)
            return config
        except RequestHumanTakeover:
            logger.critical('Request human takeover')
            exit(1)
        except Exception as e:
            logger.exception(e)
            exit(1)

    @staticmethod
    def callback(self):
        pass

    @cached_property
    def asst(self):
        if self.config.task.command != 'Maa':
            self.config.task_call('MaaStartup', True)
            if self.config.task.command != 'MaaStartup':
                self.config.task_stop()

        # Fix MaaPath=*\MAA.exe
        if os.path.isfile(self.config.MaaEmulator_MaaPath):
            path = os.path.dirname(self.config.MaaEmulator_MaaPath)
            logger.info(f'MaaEmulator_MaaPath: {self.config.MaaEmulator_MaaPath} is revised to {path}')
            self.config.MaaEmulator_MaaPath = path

        logger.info(f'MAA installation path: {self.config.MaaEmulator_MaaPath}')
        if not os.path.exists(self.config.MaaEmulator_MaaPath):
            logger.critical(
                f'Path {self.config.MaaEmulator_MaaPath} was not found. Confirm that MAA is installed there.'
                f'For first-time setup, install MAA and enter its path under MAA Settings > MAA Installation Path')
            raise RequestHumanTakeover
        try:
            incremental_path = [os.path.join(self.config.MaaEmulator_MaaPath, './cache')]
            if self.config.MaaEmulator_PackageName in ["YoStarEN", "YoStarJP", "YoStarKR", "txwy"]:
                incremental_path.append(os.path.join(
                    self.config.MaaEmulator_MaaPath,
                    './resource/global/' + self.config.MaaEmulator_PackageName)
                )
                incremental_path.append(os.path.join(
                    self.config.MaaEmulator_MaaPath,
                    './cache/resource/global/' + self.config.MaaEmulator_PackageName)
                )
            AssistantHandler.load(self.config.MaaEmulator_MaaPath, incremental_path)
        except ModuleNotFoundError:
            logger.critical('MAA was not found; verify the installation path')
            raise RequestHumanTakeover
        except OSError as e:
            # OSError: [WinError 126] The specified module could not be found.
            if '[WinError 126]' in str(e):
                logger.exception(e)
                logger.critical(
                    f'Unable to import MAA; confirm it is correctly installed at {self.config.MaaEmulator_MaaPath}'
                )
                raise RequestHumanTakeover
            else:
                raise

        @AssistantHandler.Asst.CallBackType
        def callback(msg, details, arg):
            """
            Args:
                msg (int):
                details (bytes):
                arg (c_void_p):
            """
            m = AssistantHandler.Message(msg)
            d = json.loads(details.decode('utf-8', 'ignore'))
            log_callback(m, d)
            handler = AssistantHandler.ASST_HANDLER
            if handler:
                handler.callback_timer.reset()
                for func in handler.callback_list:
                    func(m, d)

        ArknightsAutoScript.callback = callback
        asst = AssistantHandler.Asst(callback)

        asst.set_instance_option(AssistantHandler.InstanceOptionType.touch_type, self.config.MaaEmulator_TouchMethod)
        asst.set_instance_option(AssistantHandler.InstanceOptionType.adblite_enabled, '0')
        if self.config.MaaEmulator_DeploymentWithPause:
            if self.config.MaaEmulator_TouchMethod == 'maatouch':
                asst.set_instance_option(AssistantHandler.InstanceOptionType.deployment_with_pause, '1')
            else:
                logger.critical('The selected touch method does not support deploying operators while paused')
                raise RequestHumanTakeover

        return asst

    def maa_startup(self):
        AssistantHandler(config=self.config, asst=self.asst).startup()

    def maa_annihilation(self):
        AssistantHandler(config=self.config, asst=self.asst).fight()

    def maa_material(self):
        AssistantHandler(config=self.config, asst=self.asst).fight()

    def maa_fight(self):
        AssistantHandler(config=self.config, asst=self.asst).fight()

    def maa_recruit(self):
        AssistantHandler(config=self.config, asst=self.asst).recruit()

    def maa_infrast(self):
        AssistantHandler(config=self.config, asst=self.asst).infrast()

    def maa_mall(self):
        AssistantHandler(config=self.config, asst=self.asst).mall()

    def maa_award(self):
        AssistantHandler(config=self.config, asst=self.asst).award()

    def maa_roguelike(self):
        AssistantHandler(config=self.config, asst=self.asst).roguelike()

    def maa_reclamation_algorithm(self):
        AssistantHandler(config=self.config, asst=self.asst).reclamation_algorithm()


def loop(config_name):
    ArknightsAutoScript(config_name).loop()


def set_stop_event(e):
    ArknightsAutoScript.stop_event = e


def maa_copilot(config_name):
    script = ArknightsAutoScript(config_name)
    script.config.bind('MaaCopilot')
    handler = AssistantHandler(config=script.config, asst=script.asst)
    handler.connect()
    handler.copilot()
