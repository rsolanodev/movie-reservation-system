from app.payments.domain.repositories.reservation_repository import ReservationRepository
from app.payments.domain.reservation import Reservation
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository


class SqlModelReservationRepository(ReservationRepository, SqlModelRepository):
    def update(self, reservation: Reservation) -> None:
        return None
