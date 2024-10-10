import uuid
from datetime import datetime
from uuid import UUID

from app.movies.domain.movie_showtime import MovieShowtime


class MovieShowtimeFactory:
    def create(self, show_datetime: datetime, id: UUID | None = None) -> MovieShowtime:
        return MovieShowtime(id=id or uuid.uuid4(), show_datetime=show_datetime)
