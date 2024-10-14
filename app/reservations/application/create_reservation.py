from dataclasses import dataclass
from uuid import UUID

from app.reservations.domain.exceptions import SeatsNotAvailable
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import Reservation


@dataclass(frozen=True)
class CreateReservationParams:
    showtime_id: UUID
    seat_ids: list[UUID]
    user_id: UUID


class CreateReservation:
    def __init__(self, repository: ReservationRepository) -> None:
        self._repository = repository

    def execute(self, params: CreateReservationParams) -> Reservation:
        seats = self._repository.find_seats(seat_ids=params.seat_ids)

        if not seats.are_available():
            raise SeatsNotAvailable()

        reservation = Reservation.create(user_id=params.user_id, showtime_id=params.showtime_id)
        reservation.add_seats(seats)
        self._repository.save(reservation=reservation)
        return reservation
