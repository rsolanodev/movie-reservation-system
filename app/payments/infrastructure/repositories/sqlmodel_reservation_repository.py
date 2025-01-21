from sqlmodel import select

from app.payments.domain.repositories.reservation_repository import ReservationRepository
from app.payments.domain.reservation import Reservation
from app.reservations.infrastructure.models import ReservationModel
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository


class SqlModelReservationRepository(ReservationRepository, SqlModelRepository):
    def update(self, reservation: Reservation) -> None:
        reservation_model = self._session.exec(
            select(ReservationModel).where(ReservationModel.id == reservation.id.to_uuid())
        ).one()
        reservation_model.status = reservation.status.value
        self._session.add(reservation_model)
        self._session.commit()
