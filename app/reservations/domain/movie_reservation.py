from dataclasses import dataclass
from datetime import datetime

from app.shared.domain.value_objects.id import Id


@dataclass
class ReservedSeat:
    row: int
    number: int


@dataclass
class Movie:
    id: Id
    title: str
    poster_image: str | None


@dataclass
class MovieReservation:
    reservation_id: Id
    show_datetime: datetime
    movie: Movie
    seats: list[ReservedSeat]
