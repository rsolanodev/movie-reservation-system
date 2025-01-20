from app.payments.domain.finders.reservation_finder import ReservationFinder
from app.payments.domain.reservation import Reservation
from app.shared.infrastructure.finders.sqlmodel_finder import SqlModelFinder


class SqlModelReservationFinder(ReservationFinder, SqlModelFinder):
    def find_by_payment_id(self, provider_payment_id: str) -> Reservation | None:
        return None
