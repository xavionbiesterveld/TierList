import logging
import sys


def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')

        # Handler for all logs (including debug), does NOT print to stdout
        debug_file_handler = logging.FileHandler('debug.log')
        debug_file_handler.setLevel(logging.DEBUG)
        debug_file_handler.setFormatter(formatter)

        # Handler for INFO and higher (no debug), to file
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Handler for INFO and higher, to stdout
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)

        logger.addHandler(debug_file_handler)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    logger.setLevel(logging.DEBUG)  # Most permissive level to allow handlers to filter as needed
    return logger


