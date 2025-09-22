import sys
import logging

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.basicConfig(format='%(name)s: %(levelname)s: %(message)s', level=logging.DEBUG)
log = logging.getLogger('PortfolioLogger')

# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(levelname)s: %(message)s')
# console_handler.setFormatter(formatter)
# log.addHandler(console_handler)

# # Create a file handler and set its level to DEBUG
# file_handler = logging.FileHandler('debug.log')
# file_handler.setLevel(logging.DEBUG)
# file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(file_formatter)
# log.addHandler(file_handler)

def getLogger(name):
    """
    Get a new child logger.

    :param name: Name of the logger
    :return:
    """
    return logging.getLogger('PortfolioLogger.{}'.format(name))

def separator(title='', char='*', justify='left', limit=78, border=False,
              level=None, log_to_use=None):
    """
    Log a separator line for logs with options to include title, choice of
    separator character, and position. Can pass in another logger to use.

    #TODO: center and border arguments are buggy. Need to fix that..

    >>> import logging
    >>>
    >>> separator('Test title')
    >>> logging.info('testing')
    >>> ...
    >>> separator('Another Category', char='-')
    >>> logging.info('2nd Category')

    :param title: Title of separator. If None it will just display the
    characters themselves.
    :param char: Character that will be displayed.
    :param justify: Position of `title` if `title` is provided.
    :param limit: Number of characters to display.
    :param border: Whether to display a border or not.
    :param level: Log level to use. If `None`, it will use the current set
    level.
    :param log_to_use: Log to use. If None, it will use this modules logger.
    """

    log_to_use = log_to_use or log
    level = level or log_to_use.getEffectiveLevel()

    # Get character limit. If it's 'center' we'll cut it in half
    if justify == 'center':
        char_limit = int((limit / 2) - (len(log_to_use.name)/2) - (len(title)/2))
    else:
        char_limit = limit - len(log_to_use.name) - len(title)

    # Build the message
    if justify == 'left':
        message = f'{title} {char * char_limit}'
    elif justify == 'right':
        message = f'{char * char_limit} {title}'
    else:
        message = f'{char * char_limit} {title} {char * char_limit}'

    if border:
        log_to_use.log(level, char*limit)
    # Log it
    log_to_use.log(level, message)
    if border:
        log_to_use.log(level, char*limit)


