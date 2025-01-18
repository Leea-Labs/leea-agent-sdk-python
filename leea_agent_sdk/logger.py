import logging

logger = logging.getLogger('leea')

console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)
