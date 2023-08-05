from typing import Dict, List

import micropydd
from micropydd.actions import GetConfigAction, GetVersionAction, GetLoggerAction, GetLoggersAction, SetLoggerAction
from micropydd.config import ConfigService, Config
from micropydd.logger import LoggerService


class MicroPyDDModule:

    def context(self, existing_context) -> Dict:
        pass


class MicroPyDDBaseModule(MicroPyDDModule):

    def __init__(self, config_mapping: Dict) -> None:
        super().__init__()
        self._config_mapping = config_mapping

    def context(self, existing_context: Dict) -> Dict:
        super().context(existing_context)

        context = {
            LoggerService: LoggerService()
        }

        context[ConfigService] = ConfigService(
            config_mapping_dict=self._config_mapping,
            logger_service=context[LoggerService])
        context[ConfigService].set_logging_level()

        context[Config] = context[ConfigService].get_config()

        context[GetConfigAction] = GetConfigAction(context[Config])
        context[GetVersionAction] = GetVersionAction(context[Config])

        context[GetLoggerAction] = GetLoggerAction()
        context[GetLoggersAction] = GetLoggersAction()
        context[SetLoggerAction] = SetLoggerAction()
        return context


def init(config_mapping: Dict, additional_modules: List[MicroPyDDModule] = []) -> None:
    base_module = MicroPyDDBaseModule(config_mapping)

    current_context = base_module.context({})

    for module in additional_modules:
        current_context = {
            **current_context,
            **module.context(current_context)
        }

    micropydd.app_context = current_context
