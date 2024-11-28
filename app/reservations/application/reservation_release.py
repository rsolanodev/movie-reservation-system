from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.value_objects.id import ID


class ReservationRelease:
    def __init__(self, repository: ReservationRepository) -> None:
        self._repository = repository

    def execute(self, reservation_id: ID) -> None:
        reservation = self._repository.get(reservation_id)

        if not reservation.has_paid:
            return

        self._repository.release(reservation_id)
