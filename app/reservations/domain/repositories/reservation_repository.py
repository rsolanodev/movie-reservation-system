from typing import Protocol

from app.reservations.domain.reservation import Reservation


class ReservationRepository(Protocol):
    def create(self, reservation: Reservation) -> None: ...
    def release(self, reservation: Reservation) -> None: ...
