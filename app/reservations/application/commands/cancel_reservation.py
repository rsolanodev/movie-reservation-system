from dataclasses import dataclass

from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.shared.domain.value_objects.id import Id


@dataclass(frozen=True)
class CancelReservationParams:
    reservation_id: Id
    user_id: Id


class CancelReservation:
    def __init__(self, repository: ReservationRepository) -> None:
        self._repository = repository

    def execute(self, params: CancelReservationParams) -> None: ...
