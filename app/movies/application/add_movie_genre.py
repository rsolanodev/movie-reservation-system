from uuid import UUID

from app.movies.domain.exceptions import GenreAlreadyAssigned
from app.movies.domain.repositories.movie_repository import MovieRepository


class AddMovieGenre:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, movie_id: UUID, genre_id: UUID) -> None:
        movie = self._repository.get(id=movie_id)

        if movie.has_genre(genre_id=genre_id):  # type: ignore
            raise GenreAlreadyAssigned()

        self._repository.add_genre(movie_id=movie_id, genre_id=genre_id)
