from dataclasses import dataclass

from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.shared.domain.value_objects.id import ID


@dataclass(frozen=True)
class CancelReservationParams:
    reservation_id: ID
    user_id: ID


class CancelReservation:
    def __init__(self, repository: ReservationRepository) -> None:
        self._repository = repository

    def execute(self, params: CancelReservationParams) -> None: ...
