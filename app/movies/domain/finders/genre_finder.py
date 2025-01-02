from typing import Protocol

from app.movies.domain.genre import Genre


class GenreFinder(Protocol):
    def find_all(self) -> list[Genre]: ...
