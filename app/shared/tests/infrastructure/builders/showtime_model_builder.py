import uuid
from datetime import datetime

from sqlmodel import Session

from app.showtimes.infrastructure.models import ShowtimeModel


class ShowtimeModelBuilder:
    def __init__(self, session: Session) -> None:
        self._session = session

        self.id: uuid.UUID = uuid.uuid4()
        self.movie_id: uuid.UUID = uuid.uuid4()
        self.room_id: uuid.UUID = uuid.uuid4()
        self.show_datetime: datetime = datetime.now()

    def with_id(self, id: uuid.UUID) -> "ShowtimeModelBuilder":
        self.id = id
        return self

    def with_movie_id(self, movie_id: uuid.UUID) -> "ShowtimeModelBuilder":
        self.movie_id = movie_id
        return self

    def with_room_id(self, room_id: uuid.UUID) -> "ShowtimeModelBuilder":
        self.room_id = room_id
        return self

    def with_show_datetime(self, show_datetime: datetime) -> "ShowtimeModelBuilder":
        self.show_datetime = show_datetime
        return self

    def build(self) -> ShowtimeModel:
        return ShowtimeModel(
            id=self.id,
            movie_id=self.movie_id,
            room_id=self.room_id,
            show_datetime=self.show_datetime,
        )
