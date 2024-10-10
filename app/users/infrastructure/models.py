import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from app.users.domain.user import User


class UserModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    hashed_password: str

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        return UserModel(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            hashed_password=user.hashed_password,
        )

    def to_domain(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            full_name=self.full_name,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            hashed_password=self.hashed_password,
        )
