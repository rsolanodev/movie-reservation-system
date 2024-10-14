from typing import Protocol
from uuid import UUID

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.reservation import Reservation


class ReservationRepository(Protocol):
    def save(self, reservation: Reservation) -> None: ...
    def find_seats(self, seat_ids: list[UUID]) -> Seats: ...
