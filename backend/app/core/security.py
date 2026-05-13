from datetime import timedelta
from typing import Any

from jose import JWTError, jwt
from pwdlib import PasswordHash
from pydantic import BaseModel

from app.core.config import Settings
from app.utils.time import utcnow

password_hash = PasswordHash.recommended()


class TokenData(BaseModel):
    sub: str
    exp: int


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(subject: str, settings: Settings) -> str:
    expire = utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> TokenData | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return TokenData.model_validate(payload)
    except (JWTError, ValueError):
        return None
