import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.reservation import Reservation
from app.reservations.domain.seat import Seat
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus

if TYPE_CHECKING:
    from app.showtimes.infrastructure.models import ShowtimeModel
    from app.users.infrastructure.models import UserModel


class SeatModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    showtime_id: uuid.UUID = Field(foreign_key="showtimemodel.id")
    reservation_id: uuid.UUID = Field(foreign_key="reservationmodel.id", nullable=True)
    row: int
    number: int
    status: str

    showtime: "ShowtimeModel" = Relationship(back_populates="seats")
    reservation: "ReservationModel" = Relationship(back_populates="seats")

    @classmethod
    def from_domain(cls, seat: Seat) -> "SeatModel":
        return cls(id=seat.id.to_uuid(), row=seat.row, number=seat.number, status=seat.status)

    def to_domain(self) -> Seat:
        return Seat(id=Id.from_uuid(self.id), row=self.row, number=self.number, status=self.status)


class ReservationModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="usermodel.id")
    showtime_id: uuid.UUID = Field(foreign_key="showtimemodel.id")
    provider_payment_id: str | None = None
    status: str
    created_at: datetime

    showtime: "ShowtimeModel" = Relationship(back_populates="reservations")
    user: "UserModel" = Relationship(back_populates="reservations")
    seats: list["SeatModel"] = Relationship(back_populates="reservation")

    @classmethod
    def from_domain(cls, reservation: Reservation) -> "ReservationModel":
        return cls(
            id=reservation.id.to_uuid(),
            user_id=reservation.user_id.to_uuid(),
            showtime_id=reservation.showtime_id.to_uuid(),
            status=reservation.status,
            provider_payment_id=reservation.provider_payment_id,
            created_at=reservation.created_at.value,
        )

    def to_domain(self) -> Reservation:
        return Reservation(
            id=Id.from_uuid(self.id),
            user_id=Id.from_uuid(self.user_id),
            showtime_id=Id.from_uuid(self.showtime_id),
            status=ReservationStatus(self.status),
            created_at=DateTime.from_datetime(self.created_at),
            seats=Seats([]),
        )
