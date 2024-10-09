import uuid
from datetime import datetime
from uuid import UUID

from sqlmodel import Session

from app.showtimes.infrastructure.models import ShowtimeModel


class ShowtimeModelFactory:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, movie_id: UUID, show_datetime: datetime, id: UUID | None = None) -> ShowtimeModel:
        showtime_model = ShowtimeModel(id=id or uuid.uuid4(), movie_id=movie_id, show_datetime=show_datetime)
        self._session.add(showtime_model)
        return showtime_model
