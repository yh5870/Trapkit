"""로거 설정."""

import logging
import sys

from loguru import logger


def setup_logger(name: str) -> logging.Logger:
    """로거 설정."""
    # loguru 설정
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    # 표준 logging 호환
    logging_logger = logging.getLogger(name)
    logging_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logging_logger.addHandler(handler)

    return logging_logger