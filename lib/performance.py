import time
import logging

from . import logger

log = logger.getLogger(__name__)

class timer:
    """
    timer class that acts as a ContextManager and a Decorator to time
    processes. If using as a decorator, cannot use `log_*` arguments.

    >>> import time
    >>> import logging
    >>>
    >>> log = logger.getLogger('_test')
    >>>
    >>> @timer
    >>> def test():
    >>>     time.sleep(5)
    >>>
    >>> with timer('Timing sleep', log_level=logging.DEBUG, log_to_use=log) as t:
    >>>     time.sleep(5)
    >>>     t.log_time('Process 1')
    >>>     time.sleep(5)
    >>>     t.log_time('Process 2')
    """

    def __init__(self, func_or_name=None, log_level=logging.INFO, log_to_use=None,
                 *args, **kwargs):
        self.func_or_name = func_or_name

        self.log_level = log_level
        self.log_to_use = log_to_use or log

        self.start_time = None
        self._log_start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.time_unit = 'secs'

    def __enter__(self, name=None):
        self.start_timer()
        return self

    def __exit__(self, *args):
        self.end_timer()

    def __call__(self, *args, **kwargs):
        self.start_timer()
        result = self.func_or_name(*args, **kwargs)
        self.end_timer()
        return result

    def start_timer(self):
        self.start_time = time.perf_counter()

    def end_timer(self):
        self.calculate_end_time()
        self._log_message(self.func_or_name, self.elapsed_time, self.time_unit)

    def calculate_elapsed_time(self, start_time=None, end_time=None):

        start_time = start_time or self.start_time
        end_time = end_time or time.perf_counter()
        elapsed_time = end_time - start_time
        time_unit = self.time_unit

        if elapsed_time >= 60:
            elapsed_time = elapsed_time / 60
            time_unit = 'mins'
        elif elapsed_time >= 3600:
            elapsed_time = elapsed_time / 3600
            time_unit = 'hours'

        return end_time, elapsed_time, time_unit

    def calculate_end_time(self):
        self.end_time, self.elapsed_time, self.time_unit = self.calculate_elapsed_time()

    def log_time(self, name='Process'):
        _, end_time, _ = self.calculate_elapsed_time(self._log_start_time)
        self._log_start_time = time.perf_counter()
        self._log_message(name, end_time, self.time_unit)

    def _log_message(self, name, elapsed_time, time_unit):
        message = f'{name} took {elapsed_time:.3f} {time_unit} to complete.'
        self.log_to_use.log(self.log_level, message)