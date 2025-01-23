from datetime import datetime
from uuid import UUID

from sqlmodel import Session

from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.tests.infrastructure.mothers.sqlmodel_room_mother import SqlModelRoomMother
from app.shared.tests.infrastructure.mothers.sqlmodel_showtime_mother import SqlModelShowtimeMother
from app.showtimes.domain.seat import SeatStatus
from app.showtimes.domain.showtime import Showtime
from app.showtimes.infrastructure.models import ShowtimeModel
from app.showtimes.infrastructure.repositories.sqlmodel_showtime_repository import SqlModelShowtimeRepository


class TestSqlModelShowtimeRepository:
    def test_exists_showtime(self, session: Session) -> None:
        SqlModelShowtimeMother(session).create()

        assert SqlModelShowtimeRepository(session).exists(
            showtime=Showtime(
                id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                movie_id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
                room_id=Id("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=DateTime.from_datetime(datetime(2023, 4, 1, 20, 0)),
            )
        )

    def test_does_not_exist_showtime(self, session: Session) -> None:
        SqlModelShowtimeMother(session).create()

        assert not SqlModelShowtimeRepository(session).exists(
            showtime=Showtime(
                id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                movie_id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
                room_id=Id("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=DateTime.from_datetime(datetime(2023, 4, 1, 22, 0)),
            )
        )

    def test_creates_showtime_and_seats(self, session: Session) -> None:
        room = (
            SqlModelRoomMother(session)
            .with_seat_configuration([{"row": 1, "number": 2}, {"row": 3, "number": 4}])
            .create()
        )
        showtime = Showtime.create(
            movie_id=Id("ec725625-f502-4d39-9401-a415d8c1f964"),
            show_datetime=DateTime.from_datetime(datetime(2023, 4, 2, 20, 0)),
            room_id=Id.from_uuid(room.id),
        )
        SqlModelShowtimeRepository(session).create(showtime)

        showtime_model = session.get_one(ShowtimeModel, showtime.id.to_uuid())
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
        SqlModelShowtimeMother(session).create()

        SqlModelShowtimeRepository(session).delete(showtime_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"))

        showtime_model = session.get(ShowtimeModel, UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"))
        assert showtime_model is None
