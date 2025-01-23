from sqlmodel import select

from app.payments.domain.finders.reservation_finder import ReservationFinder
from app.payments.domain.reservation import Reservation
from app.reservations.infrastructure.models import ReservationModel
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus
from app.shared.infrastructure.finders.sqlmodel_finder import SqlModelFinder


class SqlModelReservationFinder(ReservationFinder, SqlModelFinder):
    def find_by_payment_id(self, provider_payment_id: str) -> Reservation | None:
        reservation_model = self._session.exec(
            select(ReservationModel).where(ReservationModel.provider_payment_id == provider_payment_id)
        ).first()
        return self._build_reservation(reservation_model) if reservation_model else None

    def _build_reservation(self, reservation_model: ReservationModel) -> Reservation:
        return Reservation(
            id=Id(reservation_model.id),
            status=ReservationStatus(reservation_model.status),
        )
