from uuid import UUID

from app.movies.domain.repositories.movie_repository import MovieRepository


class AddMovieGenre:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, movie_id: UUID, genre_id: UUID) -> None:
        self._repository.add_genre(movie_id=movie_id, genre_id=genre_id)
