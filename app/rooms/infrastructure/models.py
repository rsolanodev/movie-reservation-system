import uuid

from sqlmodel import JSON, Column, Field, SQLModel

from app.rooms.domain.entities import Room


class RoomModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    seat_configuration: list[dict[str, int]] = Field(sa_column=Column(JSON))

    @classmethod
    def from_domain(cls, room: Room) -> "RoomModel":
        return cls(id=room.id, name=room.name, seat_configuration=room.seat_configuration)
