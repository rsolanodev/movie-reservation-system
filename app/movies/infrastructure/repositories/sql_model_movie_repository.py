from uuid import UUID

from app.core.infrastructure.repositories.sql_model_repository import SqlModelRepository
from app.movies.domain.entities import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.infrastructure.models import MovieModel


class SqlModelMovieRepository(MovieRepository, SqlModelRepository):
    def save(self, movie: Movie) -> None:
        movie_model = MovieModel.from_domain(movie=movie)
        self._session.merge(movie_model)
        self._session.commit()

    def get(self, id: UUID) -> Movie:  # type: ignore
        ...
