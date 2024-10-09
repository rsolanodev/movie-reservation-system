from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.movies.domain.entities import Movie
from app.movies.domain.exceptions import MovieDoesNotExist
from app.movies.domain.repositories.movie_repository import MovieRepository


@dataclass
class RetrieveMovieParams:
    movie_id: UUID
    showtime_date: date


class RetrieveMovie:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, params: RetrieveMovieParams) -> Movie:
        movie = self._repository.get_movie_for_date(movie_id=params.movie_id, showtime_date=params.showtime_date)
        if movie is None:
            raise MovieDoesNotExist()
        return movie
