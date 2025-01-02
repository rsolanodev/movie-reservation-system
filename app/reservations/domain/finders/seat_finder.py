from typing import Protocol

from app.reservations.domain.collections.seats import Seats
from app.shared.domain.value_objects.id import Id


class SeatFinder(Protocol):
    def find_seats(self, seat_ids: list[Id]) -> Seats: ...
