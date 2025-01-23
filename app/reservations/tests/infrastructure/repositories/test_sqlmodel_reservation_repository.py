from uuid import UUID

from sqlmodel import Session

from app.reservations.domain.collections.seats import Seats
from app.reservations.infrastructure.models import ReservationModel
from app.reservations.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.reservations.tests.domain.builders.reservation_builder import ReservationBuilder
from app.reservations.tests.domain.builders.seat_builder import SeatBuilder
from app.reservations.tests.infrastructure.builders.sqlmodel_seat_builder import SqlModelSeatBuilder
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus
from app.shared.domain.value_objects.seat_status import SeatStatus
from app.shared.tests.infrastructure.builders.sqlmodel_reservation_builder import SqlModelReservationBuilder


class TestSqlModelReservationRepository:
    def test_create_reservation_and_reserve_seats(self, session: Session) -> None:
        main_seat = SqlModelSeatBuilder(session).available().build()
        parent_seat = SqlModelSeatBuilder(session).available().build()

        reservation = (
            ReservationBuilder()
            .with_user_id(Id("47d653d5-971e-42c3-86ab-2c7f40ef783a"))
            .with_showtime_id(Id("ffa502e6-8869-490c-8799-5bea26c7146d"))
            .with_provider_payment_id("pi_3MtwBwLkdIwHu7ix28a3tqPa")
            .with_seats(
                Seats(
                    [
                        SeatBuilder().with_id(Id.from_uuid(main_seat.id)).build(),
                        SeatBuilder().with_id(Id.from_uuid(parent_seat.id)).build(),
                    ]
                ),
            )
            .build()
        )

        SqlModelReservationRepository(session).create(reservation)

        reservation_model = session.get_one(ReservationModel, reservation.id.to_uuid())
        assert reservation_model.user_id == UUID("47d653d5-971e-42c3-86ab-2c7f40ef783a")
        assert reservation_model.showtime_id == UUID("ffa502e6-8869-490c-8799-5bea26c7146d")
        assert reservation_model.status == ReservationStatus.PENDING.value
        assert reservation_model.provider_payment_id == "pi_3MtwBwLkdIwHu7ix28a3tqPa"

        session.refresh(main_seat)
        assert main_seat.reservation_id == reservation.id.to_uuid()
        assert main_seat.status == SeatStatus.RESERVED.value

        session.refresh(parent_seat)
        assert parent_seat.reservation_id == reservation.id.to_uuid()
        assert parent_seat.status == SeatStatus.RESERVED.value

    def test_release_reservation(self, session: Session) -> None:
        reservation_model = SqlModelReservationBuilder(session).pending().build()
        seat_model = SqlModelSeatBuilder(session).reserved().with_reservation_id(reservation_model.id).build()

        reservation = reservation_model.to_domain()
        reservation.cancel()

        SqlModelReservationRepository(session).release(reservation=reservation)

        assert reservation_model.status == ReservationStatus.CANCELLED.value
        assert seat_model.status == SeatStatus.AVAILABLE.value
        assert seat_model.reservation_id is None

    def test_cancel_reservations_and_release_seats(self, session: Session) -> None:
        reservation_model = SqlModelReservationBuilder(session).pending().build()
        seat_model = SqlModelSeatBuilder(session).with_reservation_id(reservation_model.id).reserved().build()

        SqlModelReservationRepository(session).cancel_reservations(
            reservation_ids=[Id.from_uuid(reservation_model.id)],
        )

        assert reservation_model.status == ReservationStatus.CANCELLED.value
        assert seat_model.status == SeatStatus.AVAILABLE.value
        assert seat_model.reservation_id is None
