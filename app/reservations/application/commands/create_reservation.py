from dataclasses import dataclass

from app.reservations.domain.exceptions import SeatsNotAvailable
from app.reservations.domain.finders.seat_finder import SeatFinder
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import Reservation
from app.shared.domain.value_objects.id import Id


@dataclass(frozen=True)
class CreateReservationParams:
    showtime_id: Id
    seat_ids: list[Id]
    user_id: Id


class CreateReservation:
    def __init__(self, reservation_repository: ReservationRepository, seat_finder: SeatFinder) -> None:
        self._reservation_repository = reservation_repository
        self._seat_finder = seat_finder

    def execute(self, params: CreateReservationParams) -> Reservation:
        seats = self._seat_finder.find_seats(seat_ids=params.seat_ids)

        if not seats.are_available():
            raise SeatsNotAvailable()

        reservation = Reservation.create(user_id=params.user_id, showtime_id=params.showtime_id, seats=seats)
        self._reservation_repository.create(reservation=reservation)
        return reservation
