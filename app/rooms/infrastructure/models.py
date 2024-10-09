import uuid

from sqlmodel import JSON, Column, Field, SQLModel


class RoomModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    seat_configuration: list[dict[str, str]] = Field(sa_column=Column(JSON))
