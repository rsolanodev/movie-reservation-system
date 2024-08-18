from typing import Protocol

from app.users.domain.entities import User


class UserRepository(Protocol):
    def create(self, user: User) -> None: ...

    def find_by_email(self, email: str) -> User | None: ...
