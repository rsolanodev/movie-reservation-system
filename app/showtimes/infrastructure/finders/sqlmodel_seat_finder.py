from sqlmodel import select

from app.reservations.infrastructure.models import SeatModel
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.seat_status import SeatStatus
from app.shared.infrastructure.finders.sqlmodel_finder import SqlModelFinder
from app.showtimes.domain.finders.seat_finder import SeatFinder
from app.showtimes.domain.seat import Seat


class SqlModelSeatFinder(SeatFinder, SqlModelFinder):
    def find_seats_by_showtime_id(self, showtime_id: Id) -> list[Seat]:
        statement = (
            select(SeatModel)
            .where(SeatModel.showtime_id == showtime_id.to_uuid())
            .order_by(SeatModel.row, SeatModel.number)  # type: ignore
        )
        seat_models = self._session.exec(statement).all()
        return [self._build_seat(seat_model) for seat_model in seat_models]

    def _build_seat(self, seat_model: SeatModel) -> Seat:
        return Seat(
            id=Id.from_uuid(seat_model.id),
            row=seat_model.row,
            number=seat_model.number,
            status=SeatStatus(seat_model.status),
        )
