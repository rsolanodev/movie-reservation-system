from dataclasses import dataclass
from datetime import datetime

from app.shared.domain.value_objects.id import Id
from app.showtimes.domain.exceptions import ShowtimeAlreadyExists
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository
from app.showtimes.domain.showtime import Showtime


@dataclass
class CreateShowtimeParams:
    movie_id: Id
    room_id: Id
    show_datetime: datetime


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
