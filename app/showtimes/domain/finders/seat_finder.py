from typing import Protocol

from app.shared.domain.value_objects.id import Id
from app.showtimes.domain.seat import Seat


class SeatFinder(Protocol):
    def find_seats_by_showtime_id(self, showtime_id: Id) -> list[Seat]: ...
