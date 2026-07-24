"""JWT 토큰 생성/검증, 비밀번호 해싱."""

import bcrypt
from datetime import datetime, timedelta

from jose import JWTError, jwt

from app.config import settings


def hash_password(password: str) -> str:
    """비밀번호 해싱."""
    # bcrypt는 72바이트 제한이 있음
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증."""
    # bcrypt는 72바이트 제한이 있음
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT 토큰 생성."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> str:
    """JWT 토큰 검증 및 user_id 반환."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token")
        return user_id
    except JWTError as e:
        raise ValueError("Invalid token") from e