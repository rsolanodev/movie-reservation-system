from typing import Protocol
from uuid import UUID

from app.showtimes.domain.entities import Showtime


class MovieShowtimeRepository(Protocol):
    def get_by_movie_id(self, movie_id: UUID) -> list[Showtime]: ...
