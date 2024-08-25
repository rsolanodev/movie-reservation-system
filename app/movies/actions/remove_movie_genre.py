from uuid import UUID

from app.movies.domain.repositories.movie_repository import MovieRepository


class RemoveMovieGenre:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, movie_id: UUID, genre_id: UUID) -> None:
        self._repository.remove_genre(movie_id, genre_id)
