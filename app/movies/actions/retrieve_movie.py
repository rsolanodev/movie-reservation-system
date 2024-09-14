from uuid import UUID

from app.movies.domain.entities import Movie
from app.movies.domain.exceptions import MovieDoesNotExistException
from app.movies.domain.repositories.movie_repository import MovieRepository


class RetrieveMovie:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, id: UUID) -> Movie:
        movie = self._repository.get(id)
        if movie is None:
            raise MovieDoesNotExistException()
        return movie