from sqlmodel import Session

from app.movies.infrastructure.models import MovieModel
from app.movies.infrastructure.repositories.sql_model_movie_repository import (
    SqlModelMovieRepository,
)
from app.movies.tests.factories.movie_factory import MovieFactory


class TestSqlModelMovieRepository:
    def test_creates_movie(self, session: Session) -> None:
        movie = MovieFactory().create()

        SqlModelMovieRepository(session=session).save(movie=movie)

        movie_model = session.get(MovieModel, movie.id)

        assert movie_model is not None
        assert movie_model.title == "Deadpool & Wolverine"
        assert movie_model.description == "Deadpool and a variant of Wolverine."
        assert movie_model.poster_image == "deadpool_and_wolverine.jpg"

    def test_updates_movie(self, session: Session) -> None:
        movie = MovieFactory().create()

        session.add(MovieModel.from_domain(movie=movie))
        session.commit()

        movie.title = "The Super Mario Bros. Movie"
        movie.description = "An animated adaptation of the video game."
        movie.poster_image = "super_mario_bros.jpg"

        SqlModelMovieRepository(session=session).save(movie=movie)

        movie_model = session.get(MovieModel, movie.id)

        assert movie_model is not None
        assert movie_model.title == "The Super Mario Bros. Movie"
        assert movie_model.description == "An animated adaptation of the video game."
        assert movie_model.poster_image == "super_mario_bros.jpg"
