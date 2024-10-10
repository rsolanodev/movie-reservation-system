import uuid
from typing import TYPE_CHECKING

from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from app.rooms.domain.room import Room

if TYPE_CHECKING:
    from app.showtimes.infrastructure.models import ShowtimeModel


class RoomModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    seat_configuration: list[dict[str, int]] = Field(sa_column=Column(JSON))
    showtimes: list["ShowtimeModel"] = Relationship(back_populates="room")

    @classmethod
    def from_domain(cls, room: Room) -> "RoomModel":
        return cls(id=room.id, name=room.name, seat_configuration=room.seat_configuration)
