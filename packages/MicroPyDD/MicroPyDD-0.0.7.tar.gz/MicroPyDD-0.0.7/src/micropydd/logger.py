import logging
import uuid
import sys
from typing import List

import colorlog

from logging.handlers import TimedRotatingFileHandler

from micropydd.exceptions import LevelNameNotFoundException
from micropydd.models import Logger

LOG = logging.getLogger(__name__)

if 'flask' in sys.modules:
    import flask

DEFAULT_LOG_PATTERN = '[%(asctime)s][%(levelname)-5s]%(request_id)s[%(name)s:%(lineno)s] - %(message)s'


class ConsoleHandler(logging.StreamHandler):
    """
    Custom Console handler
    """

    def __init__(self,
                 fmt=f'%(log_color)s{DEFAULT_LOG_PATTERN}%(reset)s',
                 *args,
                 **kwargs):
        """
        Init the MicroPyConsoleHandler which extends the logging.StreamHandler

        The standard logger has also a filter wh

        :param fmt: Formatter Pattern as string or logging.Formatter
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.addFilter(RequestIdFilter())
        if isinstance(fmt, str):
            formatter = colorlog.ColoredFormatter(fmt)
        elif isinstance(fmt, logging.Formatter):
            formatter = fmt
        self.setFormatter(formatter)


class FileHandler(TimedRotatingFileHandler):
    """
    Custom Rotating File Handler
    """

    def __init__(self,
                 fmt=f'{DEFAULT_LOG_PATTERN}',
                 filename='app.log',
                 *args,
                 **kwargs):
        """
        Init the MicroPyFileHandler which extends the RotatingFileHandler

        :param fmt: Formatter Pattern as string or logging.Formatter
        :param filename:
        :param args:
        :param kwargs:
        """
        super().__init__(filename, *args, **kwargs)
        self.addFilter(RequestIdFilter())
        if isinstance(fmt, str):
            formatter = logging.Formatter(fmt)
        elif isinstance(fmt, logging.Formatter):
            formatter = fmt
        self.setFormatter(formatter)


class SysHandler(TimedRotatingFileHandler):
    """
    Custom Rotating File Handler
    """

    def __init__(self,
                 fmt='[%(asctime)s] [%(name)s] [%(levelname)s] %(request_id) s- %(message)s',
                 logging_fmt=None,
                 filename='logs/app.log',
                 *args,
                 **kwargs):
        """
        Init the MicroPyFileHandler which extends the RotatingFileHandler

        :param fmt: Formatter Pattern as string
        :param logging_fmt: Formatter instance of logging.Formatter. If it is not none it will have priority
        over fmt param
        :param filename:
        :param args:
        :param kwargs:
        """
        super().__init__(filename, *args, **kwargs)
        self.addFilter(RequestIdFilter())
        if logging_fmt is None:
            formatter = logging.Formatter(fmt)
        else:
            formatter = logging_fmt
        self.setFormatter(formatter)


class RequestIdFilter(logging.Filter):
    """
    Request Filter to log request id when coming from python
    """

    def filter(self, record):
        def generate_request_id(original_id=''):
            new_id = uuid.uuid4()

            if original_id:
                new_id = f"{original_id},{new_id}"

            return new_id

        def request_id():
            if 'flask' not in sys.modules:
                return
            if getattr(flask.g, 'request_id', None):
                return flask.g.request_id

            headers = flask.request.headers
            original_request_id = headers.get('X-Correlation-Id')
            new_uuid = generate_request_id(original_request_id)
            flask.g.request_id = new_uuid
            return new_uuid

        try:
            record.request_id = f'({request_id()})' if 'flask' in sys.modules and flask.has_request_context() else ''
        except NameError:
            record.request_id = ''
        return True


class LoggerService:
    """
    Logging Configurator instance
    """

    def __init__(self,
                 console_handler=ConsoleHandler(),
                 other_handlers=[]):
        """
        MicroPyLoggingConfigurator init method

        :param console_handler: default value is instance of class MicroPyConsoleHandler
        :param other_handlers: if you have additional handlers add to this parameter
        """
        self.console_handler = console_handler
        self.other_handlers = other_handlers

        self.init(logging.root)

    def init(self, logger):
        if self.console_handler is not None:
            logger.addHandler(self.console_handler)
        for handler in self.other_handlers:
            logger.addHandler(handler)

    @staticmethod
    def get_level(logger: str) -> str:
        """
        Get level information for a logger passed as param

        :param logger:
        :return: The level string
        """
        return logging.getLevelName(logging.getLogger(logger).level)

    @staticmethod
    def set_level(logger: str, level_name: str):
        """
        Set the level of the logger

        :param logger:
        :param level_name:
        """
        level_validation = logging._nameToLevel.get(level_name)
        if level_validation is None:
            raise LevelNameNotFoundException(logger)
        LOG.info(f'Changing logger: {logger} level to {level_name}')
        level = logging.getLevelName(level_name)
        logging.getLogger(logger).setLevel(level)
        LOG.info(f'Logger: {logger} level changed to {level_name}')

    @staticmethod
    def get_loggers() -> List[Logger]:
        """
        Retrieve all the loggers in the current context

        :return:
        """
        result = []
        loggers = logging.Logger.manager.loggerDict
        for key in loggers.keys():
            try:
                logger = LoggerService()
                logger.name = key
                logger.level = logging.getLevelName(loggers.get(key).level)
                result.append(logger)
            except Exception as e:
                LOG.warning(e)
        return result
