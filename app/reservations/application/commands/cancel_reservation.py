from dataclasses import dataclass

from app.reservations.domain.exceptions import ReservationNotFound
from app.reservations.domain.finders.reservation_finder import ReservationFinder
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.shared.domain.value_objects.id import Id


@dataclass(frozen=True)
class CancelReservationParams:
    reservation_id: Id
    user_id: Id


class CancelReservation:
    def __init__(self, finder: ReservationFinder, repository: ReservationRepository) -> None:
        self._finder = finder
        self._repository = repository

    def execute(self, params: CancelReservationParams) -> None:
        cancellable_reservation = self._finder.find_cancellable_reservation(params.reservation_id)

        if not cancellable_reservation:
            raise ReservationNotFound()

        cancellable_reservation.cancel_by_owner(user_id=params.user_id)
        self._repository.save(reservation=cancellable_reservation.reservation)
