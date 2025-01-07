from dataclasses import dataclass

from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.finders.movie_finder import MovieFinder
from app.movies.domain.movie import Movie
from app.shared.domain.value_objects.date import Date
from app.shared.domain.value_objects.id import Id


@dataclass
class FindMovieParams:
    movie_id: Id
    showtime_date: Date

    @classmethod
    def from_primitives(cls, movie_id: str, showtime_date: str) -> "FindMovieParams":
        return cls(movie_id=Id(movie_id), showtime_date=Date.from_string(showtime_date))


class FindMovie:
    def __init__(self, finder: MovieFinder) -> None:
        self._finder = finder

    def execute(self, params: FindMovieParams) -> Movie:
        movie = self._finder.find_movie_by_showtime_date(
            movie_id=params.movie_id,
            showtime_date=params.showtime_date,
        )
        if movie is None:
            raise MovieDoesNotExist()
        return movie
