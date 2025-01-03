from typing import Protocol

from app.reservations.domain.reservation import Reservation
from app.shared.domain.value_objects.id import Id


class ReservationRepository(Protocol):
    def create(self, reservation: Reservation) -> None: ...
    def release(self, reservation_id: Id) -> None: ...
