from dataclasses import dataclass

from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.showtimes.domain.exceptions import ShowtimeAlreadyExists
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository
from app.showtimes.domain.showtime import Showtime


@dataclass
class CreateShowtimeParams:
    movie_id: Id
    room_id: Id
    show_datetime: DateTime

    @classmethod
    def from_primitives(cls, movie_id: str, room_id: str, show_datetime: str) -> "CreateShowtimeParams":
        return cls(
            movie_id=Id(movie_id),
            room_id=Id(room_id),
            show_datetime=DateTime.from_string(show_datetime),
        )


class CreateShowtime:
    def __init__(self, repository: ShowtimeRepository):
        self._repository = repository

    def execute(self, params: CreateShowtimeParams) -> None:
        showtime = Showtime.create(
            movie_id=params.movie_id,
            show_datetime=params.show_datetime,
            room_id=params.room_id,
        )

        if self._repository.exists(showtime=showtime):
            raise ShowtimeAlreadyExists()

        self._repository.create(showtime=showtime)
