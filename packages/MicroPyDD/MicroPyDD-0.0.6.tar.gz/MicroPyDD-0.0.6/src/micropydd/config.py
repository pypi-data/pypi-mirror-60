import logging
import os
from typing import Dict, Type

from micropydd import VERSION
from micropydd.logger import LoggerService

LOG = logging.getLogger(__name__)


class Config:
    LOG_ROOT: int = logging.ERROR
    LOG_LEVELS: Dict[str, int] = {
        "commons": logging.ERROR
    }

    CLOUD_ENV = os.environ.get('CLOUD_ENV') or 'local'

    MICROPYDD_VERSION: str = VERSION

    EXECUTOR_WORKERS: int = 2

    def env_param(self, value, default=None):
        return os.environ.get(value) if os.environ.get(value) is None else default

    @property
    def GIT_COMMIT(self):
        return self.env_param('GIT_COMMIT')

    @property
    def GIT_BRANCH(self):
        return self.env_param('GIT_BRANCH')

    @property
    def GIT_TAG(self):
        return self.env_param('GIT_TAG')


class ConfigService:

    def __init__(self, config_mapping_dict: Dict[str, Type[Config]], logger_service: LoggerService):
        env = os.environ.get("ENV")
        if env is not None:
            self.config = config_mapping_dict[env]()
        else:
            self.config = config_mapping_dict['default']()
        self.logger_service = logger_service

    def get_config(self):
        return self.config

    def set_logging_level(self):
        logging.root.setLevel(self.config.LOG_ROOT)
        for level in self.config.LOG_LEVELS.keys():
            logging.getLogger(level).setLevel(self.config.LOG_LEVELS.get(level))
