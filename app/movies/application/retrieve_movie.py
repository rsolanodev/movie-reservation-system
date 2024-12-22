from dataclasses import dataclass

from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.movie import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.domain.value_objects.date import Date
from app.shared.domain.value_objects.id import Id


@dataclass
class RetrieveMovieParams:
    movie_id: Id
    showtime_date: Date

    @classmethod
    def from_primitive(cls, movie_id: str, showtime_date: str) -> "RetrieveMovieParams":
        return cls(movie_id=Id(movie_id), showtime_date=Date.from_string(showtime_date))


class RetrieveMovie:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, params: RetrieveMovieParams) -> Movie:
        movie = self._repository.get_movie_for_date(
            movie_id=params.movie_id,
            showtime_date=params.showtime_date,
        )
        if movie is None:
            raise MovieDoesNotExist()
        return movie
