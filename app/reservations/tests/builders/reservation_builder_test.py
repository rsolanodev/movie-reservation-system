import uuid

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.reservation import Reservation


class ReservationBuilderTest:
    def __init__(self) -> None:
        self.id: uuid.UUID = uuid.uuid4()
        self.user_id: uuid.UUID = uuid.uuid4()
        self.showtime_id: uuid.UUID = uuid.uuid4()
        self.seats: Seats = Seats([])

    def with_id(self, id: uuid.UUID) -> "ReservationBuilderTest":
        self.id = id
        return self

    def with_user_id(self, user_id: uuid.UUID) -> "ReservationBuilderTest":
        self.user_id = user_id
        return self

    def with_showtime_id(self, showtime_id: uuid.UUID) -> "ReservationBuilderTest":
        self.showtime_id = showtime_id
        return self

    def with_seats(self, seats: Seats) -> "ReservationBuilderTest":
        self.seats = seats
        return self

    def build(self) -> Reservation:
        return Reservation(id=self.id, user_id=self.user_id, showtime_id=self.showtime_id, seats=self.seats)
