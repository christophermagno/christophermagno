import logging

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.basicConfig(format='%(message)s')
log = logging.getLogger('PortfolioLogger')
log.setLevel(logging.DEBUG)

def getLogger(name):
    return logging.getLogger('PortfolioLogger.{}'.format(name))