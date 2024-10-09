from app.movies.domain.entities import Genre
from app.movies.domain.repositories.genre_repository import GenreRepository


class RetrieveGenres:
    def __init__(self, repository: GenreRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Genre]:
        return self._repository.get_all()
