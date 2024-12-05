from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.movie import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.domain.value_objects.id import Id


class DeleteMovie:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, id: Id) -> None:
        movie = self._get_or_raise_exception(id)
        self._repository.delete(id=movie.id)

    def _get_or_raise_exception(self, id: Id) -> Movie:
        movie = self._repository.get(id=id)
        if movie is None:
            raise MovieDoesNotExist()
        return movie
