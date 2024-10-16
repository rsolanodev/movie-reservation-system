from uuid import UUID

from sqlmodel import Session

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.seat import Seat, SeatStatus
from app.reservations.infrastructure.models import ReservationModel
from app.reservations.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.reservations.tests.builders.reservation_builder_test import ReservationBuilderTest
from app.reservations.tests.builders.seat_builder_test import SeatBuilderTest
from app.reservations.tests.builders.sqlmodel_seat_builder_test import SqlModelSeatBuilderTest
from app.reservations.tests.factories.sqlmodel_seat_factory_test import SqlModelSeatFactoryTest


class TestSqlModelReservationRepository:
    def test_create_reservation_and_reserve_seats(self, session: Session) -> None:
        main_seat = SqlModelSeatFactoryTest(session).create_available()
        parent_seat = SqlModelSeatFactoryTest(session).create_available()

        reservation = (
            ReservationBuilderTest()
            .with_user_id(UUID("47d653d5-971e-42c3-86ab-2c7f40ef783a"))
            .with_showtime_id(UUID("ffa502e6-8869-490c-8799-5bea26c7146d"))
            .with_seats(
                Seats(
                    [
                        SeatBuilderTest().with_id(main_seat.id).build(),
                        SeatBuilderTest().with_id(parent_seat.id).build(),
                    ]
                ),
            )
            .build()
        )

        SqlModelReservationRepository(session).create(reservation)

        reservation_model = session.get_one(ReservationModel, reservation.id)
        assert reservation_model.user_id == UUID("47d653d5-971e-42c3-86ab-2c7f40ef783a")
        assert reservation_model.showtime_id == UUID("ffa502e6-8869-490c-8799-5bea26c7146d")

        session.refresh(main_seat)
        assert main_seat.reservation_id == reservation.id
        assert main_seat.status == SeatStatus.RESERVED

        session.refresh(parent_seat)
        assert parent_seat.reservation_id == reservation.id
        assert parent_seat.status == SeatStatus.RESERVED

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

        seats = SqlModelReservationRepository(session).find_seats(
            seat_ids=[seat_available.id, seat_reserved.id],
        )

        assert seats == [
            Seat(id=seat_available.id, row=1, number=1, status=SeatStatus.AVAILABLE),
            Seat(id=seat_reserved.id, row=2, number=2, status=SeatStatus.RESERVED),
        ]
