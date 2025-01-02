from uuid import UUID

from sqlmodel import Session

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.seat import Seat, SeatStatus
from app.reservations.infrastructure.finders.sqlmodel_seat_finder import SqlModelSeatFinder
from app.reservations.tests.builders.sqlmodel_seat_builder_test import SqlModelSeatBuilderTest
from app.shared.domain.value_objects.id import Id


class TestSqlModelSeatFinder:
    def test_find_seats(self, session: Session) -> None:
        seat_available = (
            SqlModelSeatBuilderTest(session)
            .with_id(UUID("0a157516-12cd-4633-af2c-ae8d74f7edce"))
            .with_row(1)
            .with_number(1)
            .with_status(SeatStatus.AVAILABLE)
            .build()
        )
        seat_reserved = (
            SqlModelSeatBuilderTest(session)
            .with_id(UUID("a0f28786-73e6-4234-b92d-1dd7bb39cde1"))
            .with_row(2)
            .with_number(2)
            .with_status(SeatStatus.RESERVED)
            .build()
        )
        (
            SqlModelSeatBuilderTest(session)
            .with_id(UUID("20d7416a-ab97-458b-a9a2-9552ed34cf0a"))
            .with_row(3)
            .with_number(3)
            .with_status(SeatStatus.OCCUPIED)
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
