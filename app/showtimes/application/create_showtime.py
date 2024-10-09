from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.showtimes.domain.entities import Showtime
from app.showtimes.domain.exceptions import ShowtimeAlreadyExistsException
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository


@dataclass
class CreateShowtimeParams:
    movie_id: UUID
    show_datetime: datetime


class CreateShowtime:
    def __init__(self, repository: ShowtimeRepository):
        self._repository = repository

    def execute(self, params: CreateShowtimeParams) -> None:
        if self._repository.exists(params.movie_id, params.show_datetime):
            raise ShowtimeAlreadyExistsException()

        showtime = Showtime.create(movie_id=params.movie_id, show_datetime=params.show_datetime)
        self._repository.create(showtime=showtime)
