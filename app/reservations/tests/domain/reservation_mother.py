from datetime import datetime

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.reservation import Reservation, ReservationStatus
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id


class ReservationMother:
    def __init__(self) -> None:
        self._reservation = Reservation(
            id=Id("434d5682-0a19-499e-a72a-c08f47b43e09"),
            user_id=Id("6ae2c28b-fed8-4699-872b-6b889ea27bff"),
            showtime_id=Id("b109e926-104b-41d9-b314-66cf57fd66e1"),
            status=ReservationStatus.PENDING.value,
            seats=Seats(),
            provider_payment_id="pi_3MtwBwLkdIwHu7ix28a3tqPa",
            created_at=DateTime.from_datetime(datetime(2024, 12, 12, 22, 0)),
        )

    def with_status(self, status: str) -> "ReservationMother":
        self._reservation.status = status
        return self

    def create(self) -> Reservation:
        return self._reservation
