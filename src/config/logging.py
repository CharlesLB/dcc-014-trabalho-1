from __future__ import annotations

import logging
import sys
from typing import Final

LOGGER_NAME: Final = "torre_de_londres"
LOG_FORMAT: Final = "%(levelname)s %(name)s: %(message)s"


def configure_logging(*, verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
    return logger


def get_logger(suffix: str) -> logging.Logger:
    return logging.getLogger(f"{LOGGER_NAME}.{suffix}")
