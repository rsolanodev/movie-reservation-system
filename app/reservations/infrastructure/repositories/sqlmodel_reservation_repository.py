from uuid import UUID

from sqlmodel import select

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import Reservation
from app.reservations.domain.seat import SeatStatus
from app.reservations.infrastructure.models import ReservationModel, SeatModel
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository


class SqlModelReservationRepository(ReservationRepository, SqlModelRepository):
    def create(self, reservation: Reservation) -> None:
        reservation_model = ReservationModel.from_domain(reservation)
        self._session.add(reservation_model)
        self._reserve_seats(reservation)
        self._session.commit()

    def _reserve_seats(self, reservation: Reservation) -> None:
        for seat in reservation.seats:
            seat_model = self._session.get_one(SeatModel, seat.id)
            seat_model.status = SeatStatus.RESERVED
            seat_model.reservation_id = reservation.id

    def find_seats(self, seat_ids: list[UUID]) -> Seats:
        seat_models = self._session.exec(select(SeatModel).filter(SeatModel.id.in_(seat_ids))).all()  # type: ignore
        return Seats([seat_model.to_domain() for seat_model in seat_models])
