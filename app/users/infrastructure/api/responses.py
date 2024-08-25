import uuid

from pydantic import EmailStr
from sqlmodel import SQLModel


class UserResponse(SQLModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_active: bool = True
    is_superuser: bool = False
