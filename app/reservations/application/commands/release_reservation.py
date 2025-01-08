from app.reservations.domain.finders.reservation_finder import ReservationFinder
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.shared.domain.value_objects.id import Id


class ReleaseReservation:
    def __init__(self, repository: ReservationRepository, finder: ReservationFinder) -> None:
        self._repository = repository
        self._finder = finder

    def execute(self, reservation_id: Id) -> None:
        reservation = self._finder.find_reservation(reservation_id)

        if reservation.is_confirmed():
            return

        reservation.cancel()
        self._repository.release(reservation)
