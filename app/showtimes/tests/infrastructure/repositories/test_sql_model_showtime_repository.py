from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session

from app.showtimes.domain.showtime import Showtime
from app.showtimes.infrastructure.models import ShowtimeModel
from app.showtimes.infrastructure.repositories.sql_model_showtime_repository import SqlModelShowtimeRepository
from app.showtimes.tests.infrastructure.factories.showtime_model_factory import ShowtimeModelFactory


class TestSqlModelShowtimeRepository:
    def test_exists_showtime(self, session: Session) -> None:
        ShowtimeModelFactory(session=session).create(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
            movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
            show_datetime=datetime(2023, 4, 1, 20, 0, tzinfo=timezone.utc),
        )

        assert SqlModelShowtimeRepository(session=session).exists(
            showtime=Showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2023, 4, 1, 20, 0, tzinfo=timezone.utc),
            )
        )

    def test_does_not_exist_showtime(self, session: Session) -> None:
        ShowtimeModelFactory(session=session).create(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
            movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
            show_datetime=datetime(2023, 4, 1, 20, 0, tzinfo=timezone.utc),
        )

        assert not SqlModelShowtimeRepository(session=session).exists(
            showtime=Showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2023, 4, 1, 22, 0, tzinfo=timezone.utc),
            )
        )

    def test_creates_showtime(self, session: Session) -> None:
        showtime = Showtime.create(
            movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
            show_datetime=datetime(2023, 4, 2, 20, 0, tzinfo=timezone.utc),
        )
        SqlModelShowtimeRepository(session=session).create(showtime)

        showtime_model = session.get_one(ShowtimeModel, showtime.id)
        assert showtime_model.movie_id == UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        assert showtime_model.room_id == UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600")
        assert showtime_model.show_datetime == datetime(2023, 4, 2, 20, 0)

    def test_deletes_showtime(self, session: Session) -> None:
        ShowtimeModelFactory(session=session).create(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
            show_datetime=datetime(2023, 4, 1, 20, 0, tzinfo=timezone.utc),
        )

        SqlModelShowtimeRepository(session=session).delete(showtime_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"))

        showtime_model = session.get(ShowtimeModel, UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"))
        assert showtime_model is None
