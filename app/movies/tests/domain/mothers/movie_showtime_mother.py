from datetime import datetime
from typing import Self

from app.movies.domain.movie_showtime import MovieShowtime
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id


class MovieShowtimeMother:
    def __init__(self) -> None:
        self._movie_showtime = MovieShowtime(
            id=Id("d7c10c00-9598-4618-956a-ff3aa82dd33f"),
            show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
        )

    def with_id(self, id: Id) -> Self:
        self._movie_showtime.id = id
        return self

    def with_show_datetime(self, show_datetime: DateTime) -> Self:
        self._movie_showtime.show_datetime = show_datetime
        return self

    def create(self) -> MovieShowtime:
        return self._movie_showtime
