import uuid
from dataclasses import dataclass, field

from app.movies.domain.collections.movie_genres import MovieGenres
from app.movies.domain.collections.movie_showtimes import MovieShowtimes
from app.movies.domain.genre import Genre
from app.movies.domain.movie_showtime import MovieShowtime
from app.shared.domain.value_objects.id import ID


@dataclass
class Movie:
    id: ID
    title: str
    description: str | None
    poster_image: str | None

    genres: MovieGenres = field(default_factory=MovieGenres)
    showtimes: MovieShowtimes = field(default_factory=MovieShowtimes)

    @classmethod
    def create(cls, title: str, description: str | None, poster_image: str | None) -> "Movie":
        return cls(
            id=ID.from_uuid(uuid.uuid4()),
            title=title,
            description=description,
            poster_image=poster_image,
        )

    def update(self, title: str | None, description: str | None, poster_image: str | None) -> None:
        if title is not None:
            self.title = title

        if description is not None:
            self.description = description

        if poster_image is not None:
            self.poster_image = poster_image

    def add_genre(self, genre: Genre) -> None:
        self.genres.append(genre)

    def add_showtime(self, showtime: MovieShowtime) -> None:
        self.showtimes.append(showtime)

    def has_genre(self, genre_id: ID) -> bool:
        return self.genres.has_genre(genre_id=genre_id)
