import logging
from pathlib import Path

DEFAULT_PATH = Path("log.txt")

def get_logger(name: str, file_path: Path = DEFAULT_PATH) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(file_path)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(handler)

    return logger
