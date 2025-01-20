from typing import Protocol

from app.payments.domain.reservation import Reservation


class ReservationFinder(Protocol):
    def find_by_payment_id(self, provider_payment_id: str) -> Reservation | None: ...
