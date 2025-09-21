import sys
import logging

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.basicConfig(format='%(name)s: %(levelname)s: %(message)s', level=logging.INFO)
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
    return logging.getLogger('PortfolioLogger.{}'.format(name))

