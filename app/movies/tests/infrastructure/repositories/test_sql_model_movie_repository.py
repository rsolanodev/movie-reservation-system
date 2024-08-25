from sqlmodel import Session

from app.movies.domain.entities import Genre
from app.movies.infrastructure.models import GenreModel, MovieModel
from app.movies.infrastructure.repositories.sql_model_movie_repository import (
    SqlModelMovieRepository,
)
from app.movies.tests.factories.movie_factory import MovieFactory


class TestSqlModelMovieRepository:
    def test_creates_movie(self, session: Session) -> None:
        movie = MovieFactory().create()

        SqlModelMovieRepository(session=session).save(movie=movie)

        movie_model = session.get_one(MovieModel, movie.id)
        assert movie_model.title == "Deadpool & Wolverine"
        assert movie_model.description == "Deadpool and a variant of Wolverine."
        assert movie_model.poster_image == "deadpool_and_wolverine.jpg"

    def test_updates_movie(self, session: Session) -> None:
        movie = MovieFactory().create()
        session.add(MovieModel.from_domain(movie=movie))

        movie.title = "The Super Mario Bros. Movie"
        movie.description = "An animated adaptation of the video game."
        movie.poster_image = "super_mario_bros.jpg"

        SqlModelMovieRepository(session=session).save(movie=movie)

        movie_model = session.get_one(MovieModel, movie.id)
        assert movie_model.title == "The Super Mario Bros. Movie"
        assert movie_model.description == "An animated adaptation of the video game."
        assert movie_model.poster_image == "super_mario_bros.jpg"

    def test_get_movie(self, session: Session) -> None:
        expected_movie = MovieFactory().create()
        session.add(MovieModel.from_domain(movie=expected_movie))

        movie = SqlModelMovieRepository(session=session).get(id=expected_movie.id)

        assert movie == expected_movie

    def test_delete_movie(self, session: Session) -> None:
        movie = MovieFactory().create()
        session.add(MovieModel.from_domain(movie=movie))

        SqlModelMovieRepository(session=session).delete(id=movie.id)

        assert session.get(MovieModel, movie.id) is None

    def test_add_genre_to_movie(self, session: Session) -> None:
        movie = MovieFactory().create()
        genre = Genre.create(name="Action")

        session.add(MovieModel.from_domain(movie=movie))
        session.add(GenreModel.from_domain(genre=genre))

        SqlModelMovieRepository(session=session).add_genre(
            movie_id=movie.id, genre_id=genre.id
        )

        movie_model = session.get_one(MovieModel, movie.id)
        assert movie_model.genres[0].id == genre.id
        assert movie_model.genres[0].name == "Action"

    def test_remove_genre_from_movie(self, session: Session) -> None:
        movie = MovieFactory().create()
        genre = Genre.create(name="Action")

        genre_model = GenreModel.from_domain(genre=genre)
        session.add(genre_model)

        movie_model = MovieModel.from_domain(movie=movie)
        movie_model.genres.append(genre_model)
        session.add(MovieModel.from_domain(movie=movie))

        SqlModelMovieRepository(session=session).remove_genre(
            movie_id=movie.id, genre_id=genre.id
        )

        movie_model = session.get_one(MovieModel, movie.id)
        assert movie_model.genres == []
