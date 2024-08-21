import uuid

from sqlmodel import SQLModel

from app.movies.domain.entities import Movie


class MovieSchema(SQLModel):
    id: uuid.UUID
    title: str
    description: str | None
    poster_image: str | None

    @classmethod
    def from_domain(cls, movie: Movie) -> "MovieSchema":
        return cls(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            poster_image=movie.poster_image,
        )
