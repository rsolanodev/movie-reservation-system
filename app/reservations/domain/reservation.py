import uuid
from dataclasses import dataclass, field

from app.reservations.domain.collections.seats import Seats
from app.shared.domain.value_objects.id import Id


@dataclass
class Reservation:
    id: Id
    user_id: Id
    showtime_id: Id
    has_paid: bool
    seats: Seats = field(default_factory=Seats)

    @classmethod
    def create(cls, user_id: Id, showtime_id: Id) -> "Reservation":
        return cls(id=Id.from_uuid(uuid.uuid4()), user_id=user_id, showtime_id=showtime_id, has_paid=False)

    def add_seats(self, seats: Seats) -> None:
        self.seats.extend(seats)
