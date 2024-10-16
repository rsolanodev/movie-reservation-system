import uuid
from datetime import datetime
from uuid import UUID

from sqlmodel import Session

from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelShowtimeFactoryTest:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        show_datetime: datetime,
        movie_id: UUID | None = None,
        room_id: UUID | None = None,
        id: UUID | None = None,
    ) -> ShowtimeModel:
        showtime_model = ShowtimeModel(
            id=id or uuid.uuid4(),
            movie_id=movie_id or uuid.uuid4(),
            room_id=room_id or uuid.uuid4(),
            show_datetime=show_datetime,
        )
        self._session.add(showtime_model)
        return showtime_model
