from sqlmodel import SQLModel

from app.shared.domain.user import User


class UserResponse(SQLModel):
    id: str
    email: str
    full_name: str | None
    is_active: bool
    is_superuser: bool

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id.value,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )
