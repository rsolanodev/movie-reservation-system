from sqlmodel import update

from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import Reservation
from app.reservations.domain.seat import SeatStatus
from app.reservations.infrastructure.models import ReservationModel, SeatModel
from app.shared.domain.value_objects.id import Id
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository


class SqlModelReservationRepository(ReservationRepository, SqlModelRepository):
    def create(self, reservation: Reservation) -> None:
        reservation_model = ReservationModel.from_domain(reservation)
        self._session.add(reservation_model)
        self._reserve_seats(reservation)
        self._session.commit()

    def _reserve_seats(self, reservation: Reservation) -> None:
        for seat in reservation.seats:
            seat_model = self._session.get_one(SeatModel, seat.id.to_uuid())
            seat_model.status = SeatStatus.RESERVED
            seat_model.reservation_id = reservation.id.to_uuid()

    def release(self, reservation_id: Id) -> None:
        self._session.exec(
            update(SeatModel)
            .where(SeatModel.reservation_id == reservation_id.to_uuid())  # type: ignore
            .values(status=SeatStatus.AVAILABLE, reservation_id=None)
        )
        self._session.commit()
