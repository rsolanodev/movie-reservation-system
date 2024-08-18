from dataclasses import dataclass

from app.users.domain.entities import User
from app.users.domain.exceptions import UserAlreadyExistsException
from app.users.domain.repositories.user_repository import (
    UserRepository,
)


@dataclass
class CreateUserParams:
    email: str
    password: str
    full_name: str | None


class CreateUser:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, params: CreateUserParams) -> User:
        if self._repository.find_by_email(email=params.email):
            raise UserAlreadyExistsException()

        user = User.create(
            email=params.email, password=params.password, full_name=params.full_name
        )
        self._repository.create(user=user)
        return user
