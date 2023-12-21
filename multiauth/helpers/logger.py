"""Utility functions independent of the library."""

import logging
import os


def install_logger(logger: logging.Logger) -> None:
    """Install logger."""

    handler = logging.StreamHandler()

    formatter = os.getenv('LOG_FMT') or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handler.setFormatter(logging.Formatter(formatter))

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if os.getenv('DEBUG') else logging.INFO)

    # Ignore asyncio debug logs
    logging.getLogger('asyncio').setLevel(logging.ERROR)


def setup_logger(name: str | None = None) -> logging.Logger:
    """Setup logger."""

    name = name or 'multiauth'
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        install_logger(logger)

    return logger
