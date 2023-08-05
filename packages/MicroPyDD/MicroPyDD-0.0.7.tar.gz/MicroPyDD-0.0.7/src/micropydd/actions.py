import platform
import sys
import logging
from typing import List

from micropydd.config import Config
from micropydd.exceptions import LevelNotSetException
from micropydd.logger import LoggerService
from micropydd.models import Logger

LOG = logging.getLogger(__name__)


class Action:

    def __init__(self, *args, **kwargs):
        LOG.debug(f'Action {self.__class__} started')

    def execute(self, *args, **kwargs):
        pass


class GetConfigAction(Action):
    """
    Get current system configuration
    """

    def __init__(self, config: Config):
        super().__init__()
        self.config = config

    def execute(self) -> dict:
        result = {}
        for key in self.config.__dir__():
            if not (key.startswith('__') and key.endswith('__')) and \
                    not callable(getattr(self.config, key)):
                result[key] = getattr(self.config, key)
        return result


class GetVersionAction(Action):
    """
    Get current system version
    """

    def __init__(self, config: Config):
        super().__init__()
        self.config = config

    def execute(self):
        return {
            'python': {
                'version': sys.version_info,
                'implementation': platform.python_implementation(),
                'build': platform.python_build()
            },
            'platform':
                {
                    'version': platform.version(),
                    'node': platform.node(),
                    'cpu': platform.processor(),
                    'machine': platform.machine(),
                    'libc': platform.libc_ver(),
                    'uname': platform.uname()
                },
            'git': {
                'commit': self.config.GIT_COMMIT,
                'branch': self.config.GIT_BRANCH,
                'tag': self.config.GIT_TAG,
            },
        }


class GetLoggerAction(Action):
    """
    Get logger information by name
    """

    def __init__(self):
        super().__init__()

    def execute(self, name: str) -> Logger:
        super().execute()
        logger = Logger(name=name, level=LoggerService.get_level(name))
        return logger


class GetLoggersAction(Action):
    """
    Get all loggers information
    """

    def __init__(self):
        super().__init__()

    def execute(self) -> List[Logger]:
        super().execute()
        return LoggerService.get_loggers()


class SetLoggerAction(Action):
    """
    Set logger
    """

    def __init__(self):
        super().__init__()

    def execute(self, name: str, level: str) -> Logger:
        super().execute()

        LoggerService.set_level(name, level)
        final_level = LoggerService.get_level(name)
        if level != final_level:
            raise LevelNotSetException(name)
        else:
            logger = Logger(name=name, level=final_level)
            return logger
