import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.showtimes.infrastructure.models import ShowtimeModel


class RoomModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    seats: list["SeatModel"] = Relationship(back_populates="room")
    showtimes: list["ShowtimeModel"] = Relationship(back_populates="room")


class SeatModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    row: int
    number: int
    room_id: uuid.UUID = Field(foreign_key="roommodel.id")
    room: RoomModel = Relationship(back_populates="seats")
