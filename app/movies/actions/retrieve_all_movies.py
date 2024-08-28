from app.movies.domain.entities import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository


class RetrieveAllMovies:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Movie]:
        return self._repository.get_all()
