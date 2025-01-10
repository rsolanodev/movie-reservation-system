import uuid
from dataclasses import dataclass, field
from enum import StrEnum

from app.reservations.domain.collections.seats import Seats
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id


class ReservationStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class Reservation:
    id: Id
    user_id: Id
    showtime_id: Id
    status: str
    created_at: DateTime
    seats: Seats = field(default_factory=Seats)

    @classmethod
    def create(cls, user_id: Id, showtime_id: Id) -> "Reservation":
        return cls(
            id=Id.from_uuid(uuid.uuid4()),
            user_id=user_id,
            showtime_id=showtime_id,
            status=ReservationStatus.PENDING,
            created_at=DateTime.now(),
        )

    def add_seats(self, seats: Seats) -> None:
        self.seats.extend(seats)

    def is_confirmed(self) -> bool:
        return self.status == ReservationStatus.CONFIRMED

    def cancel(self) -> None:
        self.status = ReservationStatus.CANCELLED
