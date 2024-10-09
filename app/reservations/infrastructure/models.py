import uuid
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.showtimes.infrastructure.models import ShowtimeModel


class SeatStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"


class SeatModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    row: int
    number: int
    status: SeatStatus
    showtime_id: uuid.UUID = Field(foreign_key="showtimemodel.id")
    showtime: "ShowtimeModel" = Relationship(back_populates="seats")
