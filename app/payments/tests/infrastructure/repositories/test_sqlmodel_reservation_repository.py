from uuid import UUID

from sqlmodel import Session

from app.payments.domain.reservation import Reservation, ReservationStatus
from app.payments.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.shared.domain.value_objects.id import Id
from app.shared.tests.builders.sqlmodel_reservation_builder_test import SqlModelReservationBuilderTest


class TestSqlModelReservationRepository:
    def test_update_reservation(self, session: Session) -> None:
        reservation_model = (
            SqlModelReservationBuilderTest(session)
            .with_id(UUID("92ab35a6-ae79-4039-85b3-e8b2b8abb27d"))
            .with_status(ReservationStatus.PENDING.value)
            .build()
        )

        reservation = Reservation(id=Id(reservation_model.id), status=ReservationStatus.CONFIRMED)
        SqlModelReservationRepository(session).update(reservation)

        assert reservation_model.status == ReservationStatus.CONFIRMED.value
