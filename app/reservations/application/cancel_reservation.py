from dataclasses import dataclass
from uuid import UUID

from app.reservations.domain.repositories.reservation_repository import ReservationRepository


@dataclass(frozen=True)
class CancelReservationParams:
    reservation_id: UUID
    user_id: UUID


class CancelReservation:
    def __init__(self, repository: ReservationRepository) -> None:
        self._repository = repository

    def execute(self, params: CancelReservationParams) -> None: ...
