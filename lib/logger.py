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

def separator(title='', char='*', justify='left', logger=None):
    """
    Log a separator line for logs.

    :param title:
    :param char:
    :param justify:
    :param logger:
    """

    logger = logger or log
    level = logger.getEffectiveLevel()

    if justify == 'center':
        limit = int(78/2 - len(logger.name) - len(title))
    else:
        limit = 78 - len(logger.name) - len(title)

    if justify == 'left':
        message = f'{title} {char * limit}'
    elif justify == 'right':
        message = f'{char * limit} {title}'
    else:
        message = f'{char * limit} {title} {char * limit}'

    if level == logging.DEBUG:
        logger.debug(message)
    elif level == logging.INFO:
        logger.info(message)
    elif level == logging.WARNING:
        logger.warning(message)
    elif level == logging.CRITICAL:
        logger.critical(message)


