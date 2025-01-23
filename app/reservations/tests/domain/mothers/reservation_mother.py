from datetime import datetime

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.reservation import Reservation
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus


class ReservationMother:
    def __init__(self) -> None:
        self._reservation = Reservation(
            id=Id("434d5682-0a19-499e-a72a-c08f47b43e09"),
            user_id=Id("6ae2c28b-fed8-4699-872b-6b889ea27bff"),
            showtime_id=Id("b109e926-104b-41d9-b314-66cf57fd66e1"),
            status=ReservationStatus.PENDING,
            seats=Seats(),
            provider_payment_id="pi_3MtwBwLkdIwHu7ix28a3tqPa",
            created_at=DateTime.from_datetime(datetime(2024, 12, 12, 22, 0)),
        )

    def cancelled(self) -> "ReservationMother":
        self._reservation.status = ReservationStatus.CANCELLED
        return self

    def with_created_at(self, created_at: DateTime) -> "ReservationMother":
        self._reservation.created_at = created_at
        return self

    def create(self) -> Reservation:
        return self._reservation
