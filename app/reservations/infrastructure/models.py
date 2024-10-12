import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.showtimes.infrastructure.models import ShowtimeModel
    from app.users.infrastructure.models import UserModel


class SeatModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    row: int
    number: int
    status: str
    showtime_id: uuid.UUID = Field(foreign_key="showtimemodel.id")
    showtime: "ShowtimeModel" = Relationship(back_populates="seats")
    reservation_id: uuid.UUID = Field(foreign_key="reservationmodel.id", nullable=True)
    reservation: "ReservationModel" = Relationship(back_populates="seats")


class ReservationModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="usermodel.id")
    showtime_id: uuid.UUID = Field(foreign_key="showtimemodel.id")
    showtime: "ShowtimeModel" = Relationship(back_populates="reservations")
    user: "UserModel" = Relationship(back_populates="reservations")
    seats: list["SeatModel"] = Relationship(back_populates="reservation")
