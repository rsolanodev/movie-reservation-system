from uuid import UUID

from app.reservations.domain.repositories.reservation_repository import ReservationRepository


class ReservationRelease:
    def __init__(self, repository: ReservationRepository) -> None:
        self._repository = repository

    def execute(self, reservation_id: UUID) -> None:
        reservation = self._repository.get(reservation_id)

        if not reservation.has_paid:
            return

        self._repository.release(reservation_id)
