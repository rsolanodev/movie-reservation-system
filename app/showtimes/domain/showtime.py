from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from app.shared.domain.value_objects.id import Id


@dataclass
class Showtime:
    id: Id
    movie_id: Id
    room_id: Id
    show_datetime: datetime

    @classmethod
    def create(cls, movie_id: Id, room_id: Id, show_datetime: datetime) -> "Showtime":
        return cls(id=Id.from_uuid(uuid4()), movie_id=movie_id, room_id=room_id, show_datetime=show_datetime)
