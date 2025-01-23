from sqlmodel import Session

from app.payments.domain.reservation import Reservation
from app.payments.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus
from app.shared.tests.infrastructure.builders.sqlmodel_reservation_builder import SqlModelReservationBuilder


class TestSqlModelReservationRepository:
    def test_update_reservation(self, session: Session) -> None:
        reservation_model = SqlModelReservationBuilder(session).pending().build()

        reservation = Reservation(id=Id.from_uuid(reservation_model.id), status=ReservationStatus.CONFIRMED)
        SqlModelReservationRepository(session).update(reservation)

        assert reservation_model.status == ReservationStatus.CONFIRMED.value
