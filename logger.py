import logging
import sys

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        stream_handler = logging.StreamHandler(sys.stdout)
        file_handler = logging.FileHandler('app.log')
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')
        stream_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger

