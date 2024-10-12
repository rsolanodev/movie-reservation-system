import uuid
from dataclasses import dataclass, field

from app.core.domain.constants.unset import UnsetType
from app.movies.domain.collections.movie_genres import MovieGenres
from app.movies.domain.collections.movie_showtimes import MovieShowtimes
from app.movies.domain.genre import Genre
from app.movies.domain.movie_showtime import MovieShowtime


@dataclass
class Movie:
    id: uuid.UUID
    title: str
    description: str | None
    poster_image: str | None

    genres: MovieGenres = field(default_factory=MovieGenres)
    showtimes: MovieShowtimes = field(default_factory=MovieShowtimes)

    @classmethod
    def create(cls, title: str, description: str | None, poster_image: str | None) -> "Movie":
        return cls(
            id=uuid.uuid4(),
            title=title,
            description=description,
            poster_image=poster_image,
        )

    def update(
        self,
        title: str | UnsetType,
        description: str | None | UnsetType,
        poster_image: str | None | UnsetType,
    ) -> None:
        if not isinstance(title, UnsetType):
            self.title = title

        if not isinstance(description, UnsetType):
            self.description = description

        if not isinstance(poster_image, UnsetType):
            self.poster_image = poster_image

    def add_genre(self, genre: Genre) -> None:
        self.genres.append(genre)

    def add_showtime(self, showtime: MovieShowtime) -> None:
        self.showtimes.append(showtime)

    def has_genre(self, genre_id: uuid.UUID) -> bool:
        return self.genres.has_genre(genre_id=genre_id)