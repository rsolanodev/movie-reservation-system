from sqlmodel import Session

from app.movies.infrastructure.models import MovieModel
from app.movies.infrastructure.repositories.sql_model_movie_repository import (
    SqlModelMovieRepository,
)
from app.movies.tests.factories.movie_factory import MovieFactory


class TestSqlModelMovieRepository:
    def test_create_movie(self, session: Session) -> None:
        movie = MovieFactory().create()
        SqlModelMovieRepository(session=session).save(movie=movie)

        movie_model = session.get(MovieModel, movie.id)
        assert movie_model is not None
        assert movie_model.to_domain() == movie
