import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.core.config import settings

ALGORITHM = "HS256"


def _create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": subject,
        "exp": expire,
        "type": token_type,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: uuid.UUID) -> str:
    return _create_token(
        subject=str(user_id),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(user_id: uuid.UUID) -> str:
    return _create_token(
        subject=str(user_id),
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


def decode_token(token: str, expected_type: str) -> uuid.UUID:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid token")

    if payload.get("type") != expected_type:
        raise ValueError("Wrong token type")

    sub = payload.get("sub")
    if not sub:
        raise ValueError("Missing subject")

    return uuid.UUID(sub)
