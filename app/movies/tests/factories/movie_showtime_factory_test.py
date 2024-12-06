import uuid

from app.movies.domain.movie_showtime import MovieShowtime
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id


class MovieShowtimeFactoryTest:
    def create(self, show_datetime: DateTime, id: Id | None = None) -> MovieShowtime:
        return MovieShowtime(id=id or Id.from_uuid(uuid.uuid4()), show_datetime=show_datetime)
