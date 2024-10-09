from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.movies.domain.entities import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository


@dataclass(frozen=True)
class RetrieveMoviesParams:
    available_date: date
    genre_id: UUID | None = None


class RetrieveMovies:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, params: RetrieveMoviesParams) -> list[Movie]:
        movies = self._repository.get_available_movies_for_date(params.available_date)

        if params.genre_id is None:
            return movies

        movies_filtered: list[Movie] = []
        for movie in movies:
            if movie.has_genre(params.genre_id):
                movies_filtered.append(movie)

        return movies_filtered
