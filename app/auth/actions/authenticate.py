from datetime import datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

import jwt

from app.auth.domain.entities import Token, TokenType
from app.auth.domain.exceptions import (
    IncorrectPasswordException,
    UserDoesNotExistException,
    UserInactiveException,
)
from app.settings import settings
from app.users.domain.repositories.user_repository import UserRepository


class Authenticate:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, email: str, password: str) -> Token:
        user = self._repository.find_by_email(email=email)

        if not user:
            raise UserDoesNotExistException()

        if not user.verify_password(password):
            raise IncorrectPasswordException()

        if not user.is_active:
            raise UserInactiveException()

        return Token(
            access_token=self._create_access_token(user_id=user.id),
            token_type=TokenType.BEARER,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    def _create_access_token(self, user_id: UUID, algorithm: str = "HS256") -> str:
        return jwt.encode(
            payload={"exp": self._get_expire_date(), "sub": str(user_id)},
            key=settings.SECRET_KEY,
            algorithm=algorithm,
        )

    def _get_expire_date(self) -> datetime:
        return datetime.now(tz=ZoneInfo("UTC")) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
