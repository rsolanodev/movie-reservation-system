import uuid
from datetime import datetime

from app.movies.domain.movie_showtime import MovieShowtime
from app.shared.domain.value_objects.id import ID


class MovieShowtimeFactoryTest:
    def create(self, show_datetime: datetime, id: ID | None = None) -> MovieShowtime:
        return MovieShowtime(id=id or ID.from_uuid(uuid.uuid4()), show_datetime=show_datetime)
