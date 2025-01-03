from app.reservations.domain.finders.reservation_finder import ReservationFinder
from app.reservations.domain.reservation import Reservation
from app.reservations.infrastructure.models import ReservationModel
from app.shared.domain.value_objects.id import Id
from app.shared.infrastructure.finders.sqlmodel_finder import SqlModelFinder


class SqlModelReservationFinder(ReservationFinder, SqlModelFinder):
    def find_reservation(self, reservation_id: Id) -> Reservation:
        reservation_model = self._session.get_one(ReservationModel, reservation_id.to_uuid())
        return reservation_model.to_domain()
