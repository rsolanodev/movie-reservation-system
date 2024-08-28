from uuid import UUID

from sqlmodel import Session

from app.movies.domain.entities import Genre, Movie
from app.movies.infrastructure.models import MovieModel
from app.movies.infrastructure.repositories.sql_model_movie_repository import (
    SqlModelMovieRepository,
)
from app.movies.tests.factories.movie_factory import MovieFactory
from app.movies.tests.factories.sql_model_genre_factory import SqlModelGenreFactory
from app.movies.tests.factories.sql_model_movie_factory import SqlModelMovieFactory


class TestSqlModelMovieRepository:
    def test_creates_movie(self, session: Session) -> None:
        movie = MovieFactory().create()

        SqlModelMovieRepository(session=session).save(movie=movie)

        movie_model = session.get_one(MovieModel, movie.id)
        assert movie_model.title == "Deadpool & Wolverine"
        assert movie_model.description == "Deadpool and a variant of Wolverine."
        assert movie_model.poster_image == "deadpool_and_wolverine.jpg"

    def test_updates_movie(self, session: Session) -> None:
        movie_model = SqlModelMovieFactory(session).create().get()

        movie = movie_model.to_domain()
        movie.title = "The Super Mario Bros. Movie"
        movie.description = "An animated adaptation of the video game."
        movie.poster_image = "super_mario_bros.jpg"

        SqlModelMovieRepository(session=session).save(movie=movie)

        session.refresh(movie_model)
        assert movie_model.title == "The Super Mario Bros. Movie"
        assert movie_model.description == "An animated adaptation of the video game."
        assert movie_model.poster_image == "super_mario_bros.jpg"

    def test_get_movie(self, session: Session) -> None:
        SqlModelMovieFactory(session).create().add_genre()

        movie = SqlModelMovieRepository(session=session).get(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        )

        assert movie == Movie(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            title="Deadpool & Wolverine",
            description="Deadpool and a variant of Wolverine.",
            poster_image="deadpool_and_wolverine.jpg",
            genres=[
                Genre(id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"), name="Action")
            ],
        )

    def test_delete_movie(self, session: Session) -> None:
        model_movie = SqlModelMovieFactory(session).create().get()

        SqlModelMovieRepository(session=session).delete(id=model_movie.id)

        assert session.get(MovieModel, model_movie.id) is None

    def test_add_genre_to_movie(self, session: Session) -> None:
        movie_model = SqlModelMovieFactory(session).create().get()
        genre_model = SqlModelGenreFactory(session).create().get()

        SqlModelMovieRepository(session=session).add_genre(
            movie_id=movie_model.id, genre_id=genre_model.id
        )

        session.refresh(movie_model)
        assert movie_model.genres[0].id == genre_model.id
        assert movie_model.genres[0].name == "Action"

    def test_remove_genre_from_movie(self, session: Session) -> None:
        movie_model = SqlModelMovieFactory(session).create().add_genre().get()

        SqlModelMovieRepository(session=session).remove_genre(
            movie_id=movie_model.id,
            genre_id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"),
        )

        session.refresh(movie_model)
        assert movie_model.genres == []

    def test_get_all_movies(self, session: Session) -> None:
        SqlModelMovieFactory(session).create().add_genre()

        movies = SqlModelMovieRepository(session=session).get_all()

        assert movies == [
            Movie(
                id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                title="Deadpool & Wolverine",
                description="Deadpool and a variant of Wolverine.",
                poster_image="deadpool_and_wolverine.jpg",
                genres=[
                    Genre(
                        id=UUID("393210d5-80ce-4d03-b896-5d89f15aa77a"), name="Action"
                    )
                ],
            )
        ]
