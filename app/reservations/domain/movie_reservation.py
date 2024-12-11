from dataclasses import dataclass

from app.shared.domain.value_objects.date_time import DateTime
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
    show_datetime: DateTime
    movie: Movie
    seats: list[ReservedSeat]
