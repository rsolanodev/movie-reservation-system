from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum

import jwt

from app.shared.domain.value_objects.id import Id


class TokenType(StrEnum):
    BEARER = "bearer"


@dataclass
class Token:
    access_token: str
    token_type: TokenType
    expires_in: int

    @classmethod
    def create(
        cls,
        user_id: Id,
        secret_key: str,
        expire_minutes: int,
        token_type: TokenType = TokenType.BEARER,
    ) -> "Token":
        expire_date = datetime.now(tz=timezone.utc) + timedelta(minutes=expire_minutes)
        access_token = jwt.encode(
            payload={"exp": expire_date, "sub": user_id.value},
            key=secret_key,
            algorithm="HS256",
        )
        return Token(
            access_token=access_token,
            token_type=token_type,
            expires_in=expire_minutes,
        )
