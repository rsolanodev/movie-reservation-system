from typing import Protocol

from app.shared.domain.user import User


class UserFinder(Protocol):
    def find_user_by_email(self, email: str) -> User | None: ...
