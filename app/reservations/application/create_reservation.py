from dataclasses import dataclass
from datetime import timedelta

from app.reservations.domain.exceptions import SeatsNotAvailable
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import Reservation
from app.reservations.domain.schedulers.reservation_release_scheduler import ReservationReleaseScheduler
from app.shared.domain.value_objects.id import ID


@dataclass(frozen=True)
class CreateReservationParams:
    showtime_id: ID
    seat_ids: list[ID]
    user_id: ID


class CreateReservation:
    def __init__(
        self, repository: ReservationRepository, reservation_release_scheduler: ReservationReleaseScheduler
    ) -> None:
        self._repository = repository
        self._reservation_release_scheduler = reservation_release_scheduler

    def execute(self, params: CreateReservationParams) -> Reservation:
        seats = self._repository.find_seats(seat_ids=params.seat_ids)

        if not seats.are_available():
            raise SeatsNotAvailable()

        reservation = Reservation.create(user_id=params.user_id, showtime_id=params.showtime_id)
        reservation.add_seats(seats)
        self._repository.create(reservation=reservation)
        self._launch_reservation_release_task(reservation_id=reservation.id)
        return reservation

    def _launch_reservation_release_task(self, reservation_id: ID) -> None:
        self._reservation_release_scheduler.schedule(reservation_id=reservation_id, delay=timedelta(minutes=15))
