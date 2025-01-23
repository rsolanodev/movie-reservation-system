import uuid
from typing import Self

from app.movies.domain.collections.movie_genres import MovieGenres
from app.movies.domain.collections.movie_showtimes import MovieShowtimes
from app.movies.domain.genre import Genre
from app.movies.domain.movie import Movie
from app.movies.domain.movie_showtime import MovieShowtime
from app.shared.domain.value_objects.id import Id


class MovieBuilder:
    def __init__(self) -> None:
        self.id: Id = Id.from_uuid(uuid.uuid4())
        self.title: str = "Deadpool & Wolverine"
        self.description: str = "Deadpool and a variant of Wolverine."
        self.poster_image: str | None = "deadpool_and_wolverine.jpg"

        self.genres: MovieGenres = MovieGenres([])
        self.showtimes: MovieShowtimes = MovieShowtimes([])

    def with_id(self, id: Id) -> Self:
        self.id = id
        return self

    def with_title(self, title: str) -> Self:
        self.title = title
        return self

    def with_description(self, description: str) -> Self:
        self.description = description
        return self

    def with_poster_image(self, poster_image: str) -> Self:
        self.poster_image = poster_image
        return self

    def without_poster_image(self) -> Self:
        self.poster_image = None
        return self

    def with_genre(self, genre: Genre) -> Self:
        self.genres.append(genre)
        return self

    def with_showtime(self, showtime: MovieShowtime) -> Self:
        self.showtimes.append(showtime)
        return self

    def build(self) -> Movie:
        return Movie(
            id=self.id,
            title=self.title,
            description=self.description,
            poster_image=self.poster_image,
            genres=self.genres,
            showtimes=self.showtimes,
        )
