from sqlmodel import select

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.finders.seat_finder import SeatFinder
from app.reservations.infrastructure.models import SeatModel
from app.shared.domain.value_objects.id import Id
from app.shared.infrastructure.finders.sqlmodel_finder import SqlModelFinder


class SqlModelSeatFinder(SeatFinder, SqlModelFinder):
    def find_seats(self, seat_ids: list[Id]) -> Seats:
        seat_uuids = [seat_id.to_uuid() for seat_id in seat_ids]
        seat_models = self._session.exec(select(SeatModel).filter(SeatModel.id.in_(seat_uuids))).all()  # type: ignore
        return Seats([seat_model.to_domain() for seat_model in seat_models])
