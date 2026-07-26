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

    # Uvicorn 액세스 로그 설정 (Swagger UI 요청 로그 포함)
    # 핸들러가 이미 있는지 확인 후 추가
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(logging.INFO)

    # 핸들러가 아직 없을 때만 추가
    if not uvicorn_access_logger.handlers:
        uvicorn_access_handler = logging.StreamHandler(sys.stdout)
        uvicorn_access_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        uvicorn_access_logger.addHandler(uvicorn_access_handler)

    return logging_logger