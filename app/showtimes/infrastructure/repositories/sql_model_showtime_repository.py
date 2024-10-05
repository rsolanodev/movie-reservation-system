import uuid
from datetime import datetime

from sqlmodel import select

from app.core.infrastructure.repositories.sql_model_repository import SqlModelRepository
from app.showtimes.domain.entities import Showtime
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository
from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelShowtimeRepository(ShowtimeRepository, SqlModelRepository):
    def exists(self, movie_id: uuid.UUID, show_datetime: datetime) -> bool:
        statement = select(ShowtimeModel).where(
            ShowtimeModel.movie_id == movie_id,
            ShowtimeModel.show_datetime == show_datetime,
        )
        result = self._session.exec(statement).first()
        return result is not None

    def create(self, showtime: Showtime) -> None:
        showtime_model = ShowtimeModel.from_domain(showtime)
        self._session.add(showtime_model)
        self._session.commit()

    def delete(self, showtime_id: uuid.UUID) -> None:
        statement = select(ShowtimeModel).where(ShowtimeModel.id == showtime_id)
        showtime_model = self._session.exec(statement).first()
        if showtime_model:
            self._session.delete(showtime_model)
            self._session.commit()
