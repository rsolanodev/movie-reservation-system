from datetime import datetime, timezone
from typing import Self
from uuid import UUID

from sqlmodel import Session

from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelShowtimeMother:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._showtime_model = ShowtimeModel(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
            movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
            show_datetime=datetime(2023, 4, 1, 20, 0, tzinfo=timezone.utc),
        )

    def with_id(self, id: UUID) -> Self:
        self._showtime_model.id = id
        return self

    def with_movie_id(self, movie_id: UUID) -> Self:
        self._showtime_model.movie_id = movie_id
        return self

    def with_room_id(self, room_id: UUID) -> Self:
        self._showtime_model.room_id = room_id
        return self

    def with_show_datetime(self, show_datetime: datetime) -> Self:
        self._showtime_model.show_datetime = show_datetime
        return self

    def create(self) -> ShowtimeModel:
        self._session.add(self._showtime_model)
        return self._showtime_model
