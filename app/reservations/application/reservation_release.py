from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.shared.domain.value_objects.id import Id


class ReservationRelease:
    def __init__(self, repository: ReservationRepository) -> None:
        self._repository = repository

    def execute(self, reservation_id: Id) -> None:
        reservation = self._repository.get(reservation_id)

        if not reservation.has_paid:
            return

        self._repository.release(reservation_id)
