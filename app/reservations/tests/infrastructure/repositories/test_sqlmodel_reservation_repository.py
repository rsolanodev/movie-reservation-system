from uuid import UUID

from sqlmodel import Session

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.reservation import ReservationStatus
from app.reservations.domain.seat import SeatStatus
from app.reservations.infrastructure.models import ReservationModel
from app.reservations.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.reservations.tests.builders.reservation_builder_test import ReservationBuilderTest
from app.reservations.tests.builders.seat_builder_test import SeatBuilderTest
from app.reservations.tests.builders.sqlmodel_reservation_builder_test import SqlModelReservationBuilderTest
from app.reservations.tests.builders.sqlmodel_seat_builder_test import SqlModelSeatBuilderTest
from app.reservations.tests.factories.sqlmodel_seat_factory_test import SqlModelSeatFactoryTest
from app.shared.domain.value_objects.id import Id


class TestSqlModelReservationRepository:
    def test_create_reservation_and_reserve_seats(self, session: Session) -> None:
        main_seat = SqlModelSeatFactoryTest(session).create_available()
        parent_seat = SqlModelSeatFactoryTest(session).create_available()

        reservation = (
            ReservationBuilderTest()
            .with_user_id(Id("47d653d5-971e-42c3-86ab-2c7f40ef783a"))
            .with_showtime_id(Id("ffa502e6-8869-490c-8799-5bea26c7146d"))
            .with_seats(
                Seats(
                    [
                        SeatBuilderTest().with_id(Id.from_uuid(main_seat.id)).build(),
                        SeatBuilderTest().with_id(Id.from_uuid(parent_seat.id)).build(),
                    ]
                ),
            )
            .build()
        )

        SqlModelReservationRepository(session).create(reservation)

        reservation_model = session.get_one(ReservationModel, reservation.id.to_uuid())
        assert reservation_model.user_id == UUID("47d653d5-971e-42c3-86ab-2c7f40ef783a")
        assert reservation_model.showtime_id == UUID("ffa502e6-8869-490c-8799-5bea26c7146d")
        assert reservation_model.status == ReservationStatus.PENDING

        session.refresh(main_seat)
        assert main_seat.reservation_id == reservation.id.to_uuid()
        assert main_seat.status == SeatStatus.RESERVED

        session.refresh(parent_seat)
        assert parent_seat.reservation_id == reservation.id.to_uuid()
        assert parent_seat.status == SeatStatus.RESERVED

    def test_release_reservation(self, session: Session) -> None:
        reservation_model = SqlModelReservationBuilderTest(session).with_status(ReservationStatus.PENDING).build()
        seat_model = (
            SqlModelSeatBuilderTest(session)
            .with_status(SeatStatus.RESERVED)
            .with_reservation_id(reservation_model.id)
            .build()
        )

        reservation = reservation_model.to_domain()
        reservation.cancel()

        SqlModelReservationRepository(session).release(reservation=reservation)

        assert reservation_model.status == ReservationStatus.CANCELLED
        assert seat_model.status == SeatStatus.AVAILABLE
        assert seat_model.reservation_id is None
