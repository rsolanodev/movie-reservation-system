import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.shared.domain.value_objects.id import Id

if TYPE_CHECKING:
    from app.showtimes.infrastructure.models import ShowtimeModel


class MovieGenreLink(SQLModel, table=True):
    movie_id: uuid.UUID = Field(foreign_key="moviemodel.id", primary_key=True)
    genre_id: uuid.UUID = Field(foreign_key="genremodel.id", primary_key=True)


class MovieModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: str | None = None
    poster_image: str | None = None
    genres: list["GenreModel"] = Relationship(back_populates="movies", link_model=MovieGenreLink)
    showtimes: list["ShowtimeModel"] = Relationship(back_populates="movie")

    @classmethod
    def from_domain(self, movie: Movie) -> "MovieModel":
        return MovieModel(
            id=movie.id.to_uuid(),
            title=movie.title,
            description=movie.description,
            poster_image=movie.poster_image,
        )

    def to_domain(self) -> Movie:
        return Movie(
            id=Id.from_uuid(self.id),
            title=self.title,
            description=self.description,
            poster_image=self.poster_image,
        )


class GenreModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    movies: list[MovieModel] = Relationship(back_populates="genres", link_model=MovieGenreLink)

    @classmethod
    def from_domain(cls, genre: Genre) -> "GenreModel":
        return GenreModel(id=genre.id.to_uuid(), name=genre.name)

    def to_domain(self) -> Genre:
        return Genre(id=Id.from_uuid(self.id), name=self.name)
