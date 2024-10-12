import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.showtimes.infrastructure.models import ShowtimeModel


class SeatModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    row: int
    number: int
    status: str
    showtime_id: uuid.UUID = Field(foreign_key="showtimemodel.id")
    showtime: "ShowtimeModel" = Relationship(back_populates="seats")
