from typing import Protocol

from app.payments.domain.reservation import Reservation


class ReservationRepository(Protocol):
    def update(self, reservation: Reservation) -> None: ...
