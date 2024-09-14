import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Showtime:
    id: uuid.UUID
    movie_id: uuid.UUID
    show_datetime: datetime

    @classmethod
    def create(cls, movie_id: uuid.UUID, show_datetime: datetime) -> "Showtime":
        return cls(id=uuid.uuid4(), movie_id=movie_id, show_datetime=show_datetime)
