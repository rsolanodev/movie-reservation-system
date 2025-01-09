from typing import Protocol

from app.shared.domain.value_objects.id import Id
from app.showtimes.domain.showtime import Showtime


class ShowtimeRepository(Protocol):
    def exists(self, showtime: Showtime) -> bool: ...
    def create(self, showtime: Showtime) -> None: ...
    def delete(self, showtime_id: Id) -> None: ...
