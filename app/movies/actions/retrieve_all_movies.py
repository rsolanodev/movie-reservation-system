from uuid import UUID

from app.movies.domain.entities import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository


class RetrieveAllMovies:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, genre_id: UUID | None = None) -> list[Movie]:
        movies = self._repository.get_all()

        if genre_id is None:
            return movies

        return self._filter_by_genre(movies, genre_id)

    def _filter_by_genre(self, movies: list[Movie], genre_id: UUID) -> list[Movie]:
        return [movie for movie in movies if movie.has_genre(genre_id)]
