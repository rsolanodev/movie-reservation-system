from typing import Protocol
from uuid import UUID

from app.movies.domain.entities import Movie


class MovieRepository(Protocol):
    def save(self, movie: Movie) -> None: ...

    def get(self, id: UUID) -> Movie: ...
