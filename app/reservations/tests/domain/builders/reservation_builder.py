import uuid

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.reservation import Reservation, ReservationStatus
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id


class ReservationBuilder:
    def __init__(self) -> None:
        self.id: Id = Id.from_uuid(uuid.uuid4())
        self.user_id: Id = Id.from_uuid(uuid.uuid4())
        self.showtime_id: Id = Id.from_uuid(uuid.uuid4())
        self.status: str = ReservationStatus.PENDING
        self.seats: Seats = Seats([])
        self.provider_payment_id: str = "pi_3MtwBwLkdIwHu7ix28a3tqPa"
        self.created_at: DateTime = DateTime.now()

    def with_id(self, id: Id) -> "ReservationBuilder":
        self.id = id
        return self

    def with_user_id(self, user_id: Id) -> "ReservationBuilder":
        self.user_id = user_id
        return self

    def with_showtime_id(self, showtime_id: Id) -> "ReservationBuilder":
        self.showtime_id = showtime_id
        return self

    def with_seats(self, seats: Seats) -> "ReservationBuilder":
        self.seats = seats
        return self

    def with_status(self, status: ReservationStatus) -> "ReservationBuilder":
        self.status = status
        return self

    def with_created_at(self, created_at: DateTime) -> "ReservationBuilder":
        self.created_at = created_at
        return self

    def with_provider_payment_id(self, provider_payment_id: str) -> "ReservationBuilder":
        self.provider_payment_id = provider_payment_id
        return self

    def build(self) -> Reservation:
        return Reservation(
            id=self.id,
            user_id=self.user_id,
            showtime_id=self.showtime_id,
            status=self.status,
            seats=self.seats,
            provider_payment_id=self.provider_payment_id,
            created_at=self.created_at,
        )
