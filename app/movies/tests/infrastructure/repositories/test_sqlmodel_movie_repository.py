from uuid import UUID

from sqlmodel import Session

from app.movies.infrastructure.models import MovieModel
from app.movies.infrastructure.repositories.sqlmodel_movie_repository import SqlModelMovieRepository
from app.movies.tests.infrastructure.mothers.sqlmodel_genre_mother import SqlModelGenreMother
from app.movies.tests.infrastructure.mothers.sqlmodel_movie_mother import SqlModelMovieMother
from app.shared.domain.value_objects.id import Id
from app.shared.tests.domain.builders.movie_builder import MovieBuilder
from app.shared.tests.infrastructure.builders.sqlmodel_movie_builder import SqlModelMovieBuilder


class TestSqlModelMovieRepository:
    def test_creates_movie(self, session: Session) -> None:
        movie = MovieBuilder().build()

        SqlModelMovieRepository(session).save(movie=movie)

        movie_model = session.get_one(MovieModel, movie.id.to_uuid())
        assert movie_model.title == "Deadpool & Wolverine"
        assert movie_model.description == "Deadpool and a variant of Wolverine."
        assert movie_model.poster_image == "deadpool_and_wolverine.jpg"

    def test_updates_movie(self, session: Session) -> None:
        movie_model = SqlModelMovieMother(session).create()

        movie = movie_model.to_domain()
        movie.title = "The Super Mario Bros. Movie"
        movie.description = "An animated adaptation of the video game."
        movie.poster_image = "super_mario_bros.jpg"

        SqlModelMovieRepository(session).save(movie=movie)

        session.refresh(movie_model)
        assert movie_model.title == "The Super Mario Bros. Movie"
        assert movie_model.description == "An animated adaptation of the video game."
        assert movie_model.poster_image == "super_mario_bros.jpg"

    def test_delete_movie(self, session: Session) -> None:
        movie_model = SqlModelMovieMother(session).create()

        SqlModelMovieRepository(session).delete(id=Id.from_uuid(movie_model.id))

        assert session.get(MovieModel, movie_model.id) is None

    def test_add_genre_to_movie(self, session: Session) -> None:
        genre_model = SqlModelGenreMother(session).create()
        movie_model = SqlModelMovieMother(session).create()

        SqlModelMovieRepository(session).add_genre(
            movie_id=Id.from_uuid(movie_model.id), genre_id=Id.from_uuid(genre_model.id)
        )

        session.refresh(movie_model)
        assert movie_model.genres[0].id == UUID("393210d5-80ce-4d03-b896-5d89f15aa77a")
        assert movie_model.genres[0].name == "Action"

    def test_remove_genre_from_movie(self, session: Session) -> None:
        movie_model = (
            SqlModelMovieBuilder(session)
            .with_id(UUID("5a09207d-ec14-4b9f-b581-db33a7499651"))
            .with_genre(SqlModelGenreMother(session).create())
            .build()
        )

        SqlModelMovieRepository(session).remove_genre(
            movie_id=Id("5a09207d-ec14-4b9f-b581-db33a7499651"),
            genre_id=Id("393210d5-80ce-4d03-b896-5d89f15aa77a"),
        )

        session.refresh(movie_model)
        assert movie_model.genres == []
