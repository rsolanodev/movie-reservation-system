import uuid
from datetime import datetime
from typing import Self

from sqlmodel import Session

from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelShowtimeBuilder:
    def __init__(self, session: Session) -> None:
        self._session = session

        self.id: uuid.UUID = uuid.uuid4()
        self.movie_id: uuid.UUID = uuid.uuid4()
        self.room_id: uuid.UUID = uuid.uuid4()
        self.show_datetime: datetime = datetime.now()

    def with_id(self, id: uuid.UUID) -> Self:
        self.id = id
        return self

    def with_movie_id(self, movie_id: uuid.UUID) -> Self:
        self.movie_id = movie_id
        return self

    def with_room_id(self, room_id: uuid.UUID) -> Self:
        self.room_id = room_id
        return self

    def with_show_datetime(self, show_datetime: datetime) -> Self:
        self.show_datetime = show_datetime
        return self

    def build(self) -> ShowtimeModel:
        showtime_model = ShowtimeModel(
            id=self.id,
            movie_id=self.movie_id,
            room_id=self.room_id,
            show_datetime=self.show_datetime,
        )
        self._session.add(showtime_model)
        return showtime_model
