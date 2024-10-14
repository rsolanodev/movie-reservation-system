import uuid
from dataclasses import dataclass

from app.reservations.domain.collections.seats import Seats


@dataclass
class Reservation:
    id: uuid.UUID
    user_id: uuid.UUID
    showtime_id: uuid.UUID
    seats: Seats

    @classmethod
    def create(cls, user_id: uuid.UUID, showtime_id: uuid.UUID) -> "Reservation":
        return cls(id=uuid.uuid4(), user_id=user_id, showtime_id=showtime_id, seats=Seats([]))

    def add_seats(self, seats: Seats) -> None:
        self.seats.extend(seats)
