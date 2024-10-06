from uuid import UUID

from app.movies.domain.entities import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository


class RetrieveAllMovies:
    def __init__(self, repository: MovieRepository) -> None:
        self._repository = repository

    def execute(self, genre_id: UUID | None = None) -> list[Movie]:
        movies = self._repository.get_all()
        movies_filtered = self._filter_by_genre(movies, genre_id)

        for movie in movies_filtered:
            for movie_showtime in self._repository.get_showtimes(movie_id=movie.id):
                if movie_showtime.is_future():
                    movie.add_showtime(movie_showtime)

        return movies_filtered

    def _filter_by_genre(
        self, movies: list[Movie], genre_id: UUID | None
    ) -> list[Movie]:
        if genre_id is None:
            return movies

        movies_filtered: list[Movie] = []
        for movie in movies:
            if movie.has_genre(genre_id):
                movies_filtered.append(movie)
        return movies_filtered
