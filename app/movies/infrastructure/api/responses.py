from uuid import UUID

from sqlmodel import SQLModel


class GenreResponse(SQLModel):
    id: UUID
    name: str


class MovieResponse(SQLModel):
    id: UUID
    title: str
    description: str | None
    poster_image: str | None


class CreateMovieResponse(MovieResponse): ...


class UpdateMovieResponse(MovieResponse): ...


class RetrieveMovieResponse(MovieResponse):
    genres: list[GenreResponse]
