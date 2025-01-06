import uuid

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.reservation import Reservation, ReservationStatus
from app.shared.domain.value_objects.id import Id


class ReservationBuilderTest:
    def __init__(self) -> None:
        self.id: Id = Id.from_uuid(uuid.uuid4())
        self.user_id: Id = Id.from_uuid(uuid.uuid4())
        self.showtime_id: Id = Id.from_uuid(uuid.uuid4())
        self.status: str = ReservationStatus.PENDING
        self.seats: Seats = Seats([])

    def with_id(self, id: Id) -> "ReservationBuilderTest":
        self.id = id
        return self

    def with_user_id(self, user_id: Id) -> "ReservationBuilderTest":
        self.user_id = user_id
        return self

    def with_showtime_id(self, showtime_id: Id) -> "ReservationBuilderTest":
        self.showtime_id = showtime_id
        return self

    def with_seats(self, seats: Seats) -> "ReservationBuilderTest":
        self.seats = seats
        return self

    def with_status(self, status: ReservationStatus) -> "ReservationBuilderTest":
        self.status = status
        return self

    def build(self) -> Reservation:
        return Reservation(
            id=self.id,
            user_id=self.user_id,
            showtime_id=self.showtime_id,
            status=self.status,
            seats=self.seats,
        )
