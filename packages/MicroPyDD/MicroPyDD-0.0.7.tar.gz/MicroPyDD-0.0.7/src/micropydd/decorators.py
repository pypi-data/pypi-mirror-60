import inspect
import logging
import time

LOG = logging.getLogger(__name__)


def timing(f):
    def wrap(*args, **kwargs):
        time_start = time.time()
        result = f(*args, **kwargs)
        time_finish = time.time()
        inspect.getcallargs(f, *args, **kwargs)
        finish_minus_start = ((int)((time_finish - time_start)*100))/100
        message = f'Timing for function: {f.__module__}.{f.__name__} is {finish_minus_start} sec'
        LOG.debug(message)
        return result
    return wrap
