import uuid

from sqlmodel import SQLModel


class MovieResponse(SQLModel):
    id: uuid.UUID
    title: str
    description: str | None
    poster_image: str | None


class GenreResponse(SQLModel):
    id: uuid.UUID
    name: str
