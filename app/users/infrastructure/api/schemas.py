import uuid

from pydantic import EmailStr
from sqlmodel import SQLModel

from app.users.domain.entities import User


class CreateUserSchema(SQLModel):
    email: EmailStr
    password: str
    full_name: str


class UserSchema(SQLModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_active: bool = True
    is_superuser: bool = False

    @classmethod
    def from_domain(cls, user: User) -> "UserSchema":
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )
