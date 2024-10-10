from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class CreateShowtimePayload(SQLModel):
    movie_id: UUID
    room_id: UUID
    show_datetime: datetime
