from datetime import datetime, timezone
from unittest.mock import ANY
from uuid import UUID

from sqlmodel import Session

from app.shared.tests.builders.sqlmodel_movie_builder_test import SqlModelMovieBuilderTest
from app.shared.tests.factories.sqlmodel_room_factory_test import SqlModelRoomFactoryTest
from app.showtimes.domain.seat import Seat, SeatStatus
from app.showtimes.domain.showtime import Showtime
from app.showtimes.infrastructure.models import ShowtimeModel
from app.showtimes.infrastructure.repositories.sqlmodel_showtime_repository import SqlModelShowtimeRepository
from app.showtimes.tests.factories.sqlmodel_seat_factory_test import SqlModelSeatFactoryTest
from app.showtimes.tests.factories.sqlmodel_showtime_factory_test import SqlModelShowtimeFactoryTest


class TestSqlModelShowtimeRepository:
    def test_exists_showtime(self, session: Session) -> None:
        SqlModelShowtimeFactoryTest(session=session).create(
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
        SqlModelShowtimeFactoryTest(session=session).create(
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

    def test_creates_showtime_and_seats_to_reserve(self, session: Session) -> None:
        room = SqlModelRoomFactoryTest(session=session).create(
            id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
            name="Room 1",
            seat_configuration=[{"row": 1, "number": 2}, {"row": 3, "number": 4}],
        )
        showtime = Showtime.create(
            movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            show_datetime=datetime(2023, 4, 2, 20, 0, tzinfo=timezone.utc),
            room_id=room.id,
        )
        SqlModelShowtimeRepository(session=session).create(showtime)

        showtime_model = session.get_one(ShowtimeModel, showtime.id)
        assert showtime_model.movie_id == UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        assert showtime_model.room_id == UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600")
        assert showtime_model.show_datetime == datetime(2023, 4, 2, 20, 0)

        assert showtime_model.seats[0].row == 1
        assert showtime_model.seats[0].number == 2
        assert showtime_model.seats[0].status == SeatStatus.AVAILABLE

        assert showtime_model.seats[1].row == 3
        assert showtime_model.seats[1].number == 4
        assert showtime_model.seats[1].status == SeatStatus.AVAILABLE

    def test_deletes_showtime(self, session: Session) -> None:
        SqlModelShowtimeFactoryTest(session=session).create(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
            show_datetime=datetime(2023, 4, 1, 20, 0, tzinfo=timezone.utc),
        )

        SqlModelShowtimeRepository(session=session).delete(showtime_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"))

        showtime_model = session.get(ShowtimeModel, UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"))
        assert showtime_model is None

    def test_retrieves_seats_ordered_by_row_and_number(self, session: Session) -> None:
        showtime_id = UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601")

        SqlModelMovieBuilderTest(session=session).with_id(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            id=showtime_id,
            show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
        ).build()

        seat_model_factory = SqlModelSeatFactoryTest(session=session)
        seat_model_factory.create(showtime_id=showtime_id, row=2, number=1, status=SeatStatus.OCCUPIED)
        seat_model_factory.create(showtime_id=showtime_id, row=1, number=1, status=SeatStatus.AVAILABLE)
        seat_model_factory.create(showtime_id=showtime_id, row=1, number=2, status=SeatStatus.RESERVED)
        seat_model_factory.create(row=1, number=1)

        seats = SqlModelShowtimeRepository(session=session).retrive_seats(showtime_id=showtime_id)

        assert seats == [
            Seat(id=ANY, row=1, number=1, status=SeatStatus.AVAILABLE),
            Seat(id=ANY, row=1, number=2, status=SeatStatus.RESERVED),
            Seat(id=ANY, row=2, number=1, status=SeatStatus.OCCUPIED),
        ]
