from typing import Protocol

from app.movies.domain.entities import Category


class CategoryRepository(Protocol):
    def get_all(self) -> list[Category]: ...
