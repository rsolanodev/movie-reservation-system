from app.shared.domain.value_objects.id import Id
from app.showtimes.domain.finders.seat_finder import SeatFinder
from app.showtimes.domain.seat import Seat


class FindSeats:
    def __init__(self, finder: SeatFinder) -> None:
        self._finder = finder

    def execute(self, showtime_id: Id) -> list[Seat]:
        return self._finder.find_seats_by_showtime_id(showtime_id=showtime_id)
