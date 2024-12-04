from dataclasses import dataclass
from datetime import date

from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.movie import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.domain.value_objects.id import ID


@dataclass
class RetrieveMovieParams:
    movie_id: ID
    showtime_date: date

    @classmethod
    def from_primitives(cls, movie_id: str, showtime_date: date) -> "RetrieveMovieParams":
        return cls(movie_id=ID(movie_id), showtime_date=showtime_date)


class RetrieveMovie:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, params: RetrieveMovieParams) -> Movie:
        movie = self._repository.get_movie_for_date(movie_id=params.movie_id, showtime_date=params.showtime_date)
        if movie is None:
            raise MovieDoesNotExist()
        return movie
