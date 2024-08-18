from typing import Protocol

from app.movies.domain.entities import Movie


class MovieRepository(Protocol):
    def save(self, movie: Movie) -> None: ...
