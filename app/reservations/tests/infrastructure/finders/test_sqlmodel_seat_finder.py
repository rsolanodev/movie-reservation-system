from uuid import UUID

from sqlmodel import Session

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.seat import Seat
from app.reservations.infrastructure.finders.sqlmodel_seat_finder import SqlModelSeatFinder
from app.reservations.tests.infrastructure.builders.sqlmodel_seat_builder import SqlModelSeatBuilder
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.seat_status import SeatStatus


class TestSqlModelSeatFinder:
    def test_find_seats(self, session: Session) -> None:
        seat_available = (
            SqlModelSeatBuilder(session)
            .with_id(UUID("0a157516-12cd-4633-af2c-ae8d74f7edce"))
            .with_row(1)
            .with_number(1)
            .available()
            .build()
        )
        seat_reserved = (
            SqlModelSeatBuilder(session)
            .with_id(UUID("a0f28786-73e6-4234-b92d-1dd7bb39cde1"))
            .with_row(2)
            .with_number(2)
            .reserved()
            .build()
        )
        (
            SqlModelSeatBuilder(session)
            .with_id(UUID("20d7416a-ab97-458b-a9a2-9552ed34cf0a"))
            .with_row(3)
            .with_number(3)
            .occupied()
            .build()
        )

        seats = SqlModelSeatFinder(session).find_seats(
            seat_ids=[Id.from_uuid(seat_available.id), Id.from_uuid(seat_reserved.id)],
        )

        assert seats == Seats(
            [
                Seat(id=Id.from_uuid(seat_available.id), row=1, number=1, status=SeatStatus.AVAILABLE),
                Seat(id=Id.from_uuid(seat_reserved.id), row=2, number=2, status=SeatStatus.RESERVED),
            ]
        )
