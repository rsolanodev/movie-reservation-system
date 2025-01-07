from dataclasses import dataclass

from app.movies.domain.finders.movie_finder import MovieFinder
from app.movies.domain.movie import Movie
from app.shared.domain.value_objects.date import Date
from app.shared.domain.value_objects.id import Id


@dataclass(frozen=True)
class FindMoviesParams:
    showtime_date: Date
    genre_id: Id | None

    @classmethod
    def from_primitives(cls, showtime_date: str, genre_id: str | None = None) -> "FindMoviesParams":
        return cls(
            showtime_date=Date.from_string(showtime_date),
            genre_id=Id(genre_id) if genre_id else None,
        )


class FindMovies:
    def __init__(self, finder: MovieFinder) -> None:
        self._finder = finder

    def execute(self, params: FindMoviesParams) -> list[Movie]:
        movies = self._finder.find_movies_by_showtime_date(params.showtime_date)

        if params.genre_id is None:
            return movies

        movies_filtered: list[Movie] = []
        for movie in movies:
            if movie.has_genre(params.genre_id):
                movies_filtered.append(movie)

        return movies_filtered
