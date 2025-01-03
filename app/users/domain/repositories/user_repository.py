from typing import Protocol

from app.shared.domain.user import User


class UserRepository(Protocol):
    def create(self, user: User) -> None: ...
