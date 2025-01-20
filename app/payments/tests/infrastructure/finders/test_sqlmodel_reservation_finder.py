from uuid import UUID

from sqlmodel import Session

from app.payments.domain.reservation import Reservation, ReservationStatus
from app.payments.infrastructure.finders.sqlmodel_reservation_finder import SqlModelReservationFinder
from app.shared.domain.value_objects.id import Id
from app.shared.tests.builders.sqlmodel_reservation_builder_test import SqlModelReservationBuilderTest


class TestSqlModelReservationFinder:
    def test_find_reservation_by_payment_id(self, session: Session) -> None:
        (
            SqlModelReservationBuilderTest(session)
            .with_id(UUID("92ab35a6-ae79-4039-85b3-e8b2b8abb27d"))
            .with_provider_payment_id("pi_3MtwBwLkdIwHu7ix28a3tqPa")
            .with_status(ReservationStatus.PENDING.value)
            .build()
        )

        reservation = SqlModelReservationFinder(session).find_by_payment_id(
            provider_payment_id="pi_3MtwBwLkdIwHu7ix28a3tqPa"
        )

        assert reservation == Reservation(
            id=Id("92ab35a6-ae79-4039-85b3-e8b2b8abb27d"), status=ReservationStatus.PENDING
        )
