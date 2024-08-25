from pydantic import EmailStr
from sqlmodel import SQLModel


class CreateUserPayload(SQLModel):
    email: EmailStr
    password: str
    full_name: str
