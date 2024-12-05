from app.movies.domain.exceptions import GenreNotAssigned
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.domain.value_objects.id import Id


class RemoveMovieGenre:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, movie_id: Id, genre_id: Id) -> None:
        movie = self._repository.get(id=movie_id)

        if not movie.has_genre(genre_id=genre_id):  # type: ignore
            raise GenreNotAssigned()

        self._repository.remove_genre(movie_id, genre_id)
