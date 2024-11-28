from dataclasses import dataclass

from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.value_objects.id import ID


@dataclass(frozen=True)
class CancelReservationParams:
    reservation_id: ID
    user_id: ID

    @classmethod
    def from_primitives(cls, reservation_id: str, user_id: str) -> "CancelReservationParams":
        return cls(reservation_id=ID(reservation_id), user_id=ID(user_id))


class CancelReservation:
    def __init__(self, repository: ReservationRepository) -> None:
        self._repository = repository

    def execute(self, params: CancelReservationParams) -> None: ...
