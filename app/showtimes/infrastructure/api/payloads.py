from datetime import datetime

from sqlmodel import SQLModel


class CreateShowtimePayload(SQLModel):
    movie_id: str
    room_id: str
    show_datetime: datetime
