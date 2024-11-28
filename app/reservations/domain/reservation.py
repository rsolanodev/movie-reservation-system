import uuid
from dataclasses import dataclass, field

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.value_objects.id import ID


@dataclass
class Reservation:
    id: ID
    user_id: ID
    showtime_id: ID
    has_paid: bool
    seats: Seats = field(default_factory=Seats)

    @classmethod
    def create(cls, user_id: ID, showtime_id: ID) -> "Reservation":
        return cls(id=ID.from_uuid(uuid.uuid4()), user_id=user_id, showtime_id=showtime_id, has_paid=False)

    def add_seats(self, seats: Seats) -> None:
        self.seats.extend(seats)
