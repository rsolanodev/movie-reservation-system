import uuid

from sqlmodel import SQLModel


class GenreResponse(SQLModel):
    id: uuid.UUID
    name: str


class MovieResponse(SQLModel):
    id: uuid.UUID
    title: str
    description: str | None
    poster_image: str | None


class MovieDetailResponse(SQLModel):
    id: uuid.UUID
    title: str
    description: str | None
    poster_image: str | None
    genres: list[GenreResponse]
