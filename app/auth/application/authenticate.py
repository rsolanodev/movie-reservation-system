from app.auth.domain.entities import Token
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

        if user is None:
            raise UserDoesNotExistException()

        if user.verify_password(password) is False:
            raise IncorrectPasswordException()

        if user.is_active is False:
            raise UserInactiveException()

        return Token.create(
            user_id=user.id,
            secret_key=settings.SECRET_KEY,
            expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
