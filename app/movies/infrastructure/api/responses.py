from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

from app.movies.domain.movie import Movie


class GenreResponse(SQLModel):
    id: UUID
    name: str


class MovieResponse(SQLModel):
    id: UUID
    title: str
    description: str | None
    poster_image: str | None


class MovieShowtimeResponse(SQLModel):
    id: UUID
    show_datetime: datetime


class CreateMovieResponse(MovieResponse): ...


class UpdateMovieResponse(MovieResponse):
    @classmethod
    def from_domain(cls, movie: Movie) -> "UpdateMovieResponse":
        return cls(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            poster_image=movie.poster_image,
        )


class RetrieveMovieResponse(MovieResponse):
    genres: list[GenreResponse]
    showtimes: list[MovieShowtimeResponse]
