from dataclasses import dataclass
from datetime import date

from app.movies.domain.movie import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.shared.domain.value_objects.id import ID


@dataclass(frozen=True)
class RetrieveMoviesParams:
    available_date: date
    genre_id: ID | None

    @classmethod
    def from_primitives(cls, available_date: date, genre_id: str | None) -> "RetrieveMoviesParams":
        return cls(available_date=available_date, genre_id=ID(genre_id) if genre_id else None)


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
