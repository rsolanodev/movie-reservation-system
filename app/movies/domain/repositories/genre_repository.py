from typing import Protocol

from app.movies.domain.entities import Genre


class GenreRepository(Protocol):
    def get_all(self) -> list[Genre]: ...
