import uuid

from sqlmodel import Field, SQLModel

from app.movies.domain.entities import Movie


class MovieModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: str | None = None
    poster_image: str | None = None

    @classmethod
    def from_domain(self, movie: Movie) -> "MovieModel":
        return MovieModel(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            poster_image=movie.poster_image,
        )

    def to_domain(self) -> Movie:
        return Movie(
            id=self.id,
            title=self.title,
            description=self.description,
            poster_image=self.poster_image,
        )
