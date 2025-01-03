from dataclasses import dataclass

from app.shared.domain.finders.user_finder import UserFinder
from app.shared.domain.user import User
from app.users.domain.exceptions import UserAlreadyExists
from app.users.domain.repositories.user_repository import UserRepository


@dataclass
class CreateUserParams:
    email: str
    password: str
    full_name: str | None


class CreateUser:
    def __init__(self, repository: UserRepository, finder: UserFinder) -> None:
        self._repository = repository
        self._finder = finder

    def execute(self, params: CreateUserParams) -> User:
        if self._finder.find_user_by_email(email=params.email):
            raise UserAlreadyExists()

        user = User.create(email=params.email, password=params.password, full_name=params.full_name)
        self._repository.create(user=user)
        return user
