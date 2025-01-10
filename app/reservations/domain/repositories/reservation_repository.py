from typing import Protocol

from app.reservations.domain.reservation import Reservation
from app.shared.domain.value_objects.id import Id


class ReservationRepository(Protocol):
    def create(self, reservation: Reservation) -> None: ...
    def release(self, reservation: Reservation) -> None: ...
    def cancel_reservations(self, reservation_ids: list[Id]) -> None: ...
