import logging
import sys


def setup_logging(
    level: str = "DEBUG",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
):
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    root_logger.handlers.clear()

    formatter = logging.Formatter(log_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    return root_logger

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)