import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReservedSeat:
    row: int
    number: int


@dataclass
class Movie:
    id: uuid.UUID
    title: str
    poster_image: str | None


@dataclass
class MovieReservation:
    reservation_id: uuid.UUID
    show_datetime: datetime
    movie: Movie
    seats: list[ReservedSeat]
