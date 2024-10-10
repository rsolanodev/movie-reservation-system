import uuid
from dataclasses import dataclass

from passlib.context import CryptContext


@dataclass
class User:
    id: uuid.UUID
    email: str
    full_name: str | None
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False

    @classmethod
    def create(cls, email: str, full_name: str | None, password: str) -> "User":
        return cls(
            id=uuid.uuid4(),
            email=email,
            full_name=full_name,
            hashed_password=cls._hash_password(password),
        )

    @staticmethod
    def _hash_password(password: str) -> str:
        return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)

    def verify_password(self, password: str) -> bool:
        return CryptContext(schemes=["bcrypt"]).verify(password, self.hashed_password)

    def mark_as_inactive(self) -> None:
        self.is_active = False
