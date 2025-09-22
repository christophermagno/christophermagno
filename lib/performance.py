import time
from . import logger

log = logger.getLogger(__name__)

class timer:
    def __init__(self, func_or_name=None, *args, **kwargs):
        self.func_or_name = func_or_name
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.time_unit = 'secs'

    def start_timer(self):
        self.start_time = time.perf_counter()

    def end_timer(self):
        self.end_time = time.perf_counter()
        self.calculate_elapsed_time()
        message = f'"{self.func_or_name}" took ' if self.func_or_name else 'Took '
        message += f'{self.elapsed_time:.3f} {self.time_unit} to complete.'
        log.debug(message)

    def calculate_elapsed_time(self):

        self.elapsed_time = self.end_time - self.start_time
        if self.elapsed_time >= 60:
            self.elapsed_time = self.elapsed_time / 60
            self.time_unit = 'mins'
        elif self.elapsed_time >= 3600:
            self.elapsed_time = self.elapsed_time / 3600
            self.time_unit = 'hours'

    def __enter__(self, name=None):
        if name is None:
            name = self.func_or_name
        self.start_timer()

    def __exit__(self, *args):
        self.end_timer()

    def __call__(self, *args, **kwargs):
        self.start_timer()
        result = self.func_or_name(*args, **kwargs)
        self.end_timer()
        return result