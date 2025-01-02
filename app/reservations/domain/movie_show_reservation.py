from dataclasses import dataclass

from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id


@dataclass
class SeatLocation:
    row: int
    number: int


@dataclass
class Movie:
    id: Id
    title: str
    poster_image: str | None


@dataclass
class MovieShowReservation:
    reservation_id: Id
    show_datetime: DateTime
    movie: Movie
    seats: list[SeatLocation]
