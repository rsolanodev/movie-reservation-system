import uuid
from datetime import datetime

from sqlmodel import Session

from app.movies.tests.factories.sql_model_movie_factory import SqlModelMovieFactory
from app.showtimes.domain.entities import Showtime
from app.showtimes.infrastructure.models import ShowtimeModel
from app.showtimes.infrastructure.repositories.sql_model_showtime_repository import (
    SqlModelShowtimeRepository,
)


class TestSqlModelShowtimeRepository:
    def test_exists_showtime(self, session: Session) -> None:
        movie_model = (
            SqlModelMovieFactory(session=session)
            .create()
            .add_showtime(datetime(2023, 4, 1, 20, 0))
            .get()
        )

        repository = SqlModelShowtimeRepository(session=session)
        assert repository.exists(movie_model.id, datetime(2023, 4, 1, 20, 0)) is True

    def test_does_not_exist_showtime(self, session: Session) -> None:
        movie_model = SqlModelMovieFactory(session=session).create().get()

        repository = SqlModelShowtimeRepository(session=session)
        assert repository.exists(movie_model.id, datetime(2023, 4, 2, 20, 0)) is False

    def test_create_showtime(self, session: Session) -> None:
        movie_model = SqlModelMovieFactory(session=session).create().get()
        showtime = Showtime.create(
            movie_id=movie_model.id, show_datetime=datetime(2023, 4, 2, 20, 0)
        )

        SqlModelShowtimeRepository(session=session).create(showtime)

        showtime_model = session.get(ShowtimeModel, showtime.id)
        assert showtime_model is not None
        assert showtime_model.movie_id == movie_model.id
        assert showtime_model.show_datetime == datetime(2023, 4, 2, 20, 0)

    def test_delete_showtime(self, session: Session) -> None:
        SqlModelMovieFactory(session=session).create().add_showtime(
            datetime(2023, 4, 2, 20, 0)
        ).get()

        SqlModelShowtimeRepository(session=session).delete(
            showtime_id=uuid.UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600")
        )

        showtime_model = session.get(
            ShowtimeModel, uuid.UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600")
        )
        assert showtime_model is None

    def test_get_showtimes_by_movie_id(self, session: Session) -> None:
        movie_model = (
            SqlModelMovieFactory(session=session)
            .create()
            .add_showtime(datetime(2023, 4, 3, 20, 0))
            .get()
        )

        repository = SqlModelShowtimeRepository(session=session)
        showtimes = repository.get_by_movie_id(movie_model.id)

        assert showtimes == [
            Showtime(
                id=uuid.UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                movie_id=movie_model.id,
                show_datetime=datetime(2023, 4, 3, 20, 0),
            ),
        ]

    def test_get_by_movie_id_no_showtimes(self, session: Session) -> None:
        SqlModelMovieFactory(session=session).create().get()

        repository = SqlModelShowtimeRepository(session=session)
        showtimes = repository.get_by_movie_id(
            movie_id=uuid.UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600")
        )

        assert showtimes == []
