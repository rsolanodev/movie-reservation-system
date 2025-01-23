import uuid
from dataclasses import dataclass

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.exceptions import CancellationNotAllowed, UnauthorizedCancellation
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus


@dataclass
class Reservation:
    id: Id
    user_id: Id
    showtime_id: Id
    status: ReservationStatus
    seats: Seats
    provider_payment_id: str | None
    created_at: DateTime

    @classmethod
    def create(
        cls, user_id: Id, showtime_id: Id, provider_payment_id: str, seats: Seats | None = None
    ) -> "Reservation":
        return cls(
            id=Id.from_uuid(uuid.uuid4()),
            user_id=user_id,
            showtime_id=showtime_id,
            status=ReservationStatus.PENDING,
            seats=seats or Seats(),
            provider_payment_id=provider_payment_id,
            created_at=DateTime.now(),
        )

    def cancel(self) -> None:
        self.status = ReservationStatus.CANCELLED


@dataclass
class CancellableReservation:
    reservation: Reservation
    show_datetime: DateTime

    @property
    def user_id(self) -> Id:
        return self.reservation.user_id

    def cancel_by_owner(self, user_id: Id) -> None:
        if self.user_id != user_id:
            raise UnauthorizedCancellation()

        if DateTime.now() >= self.show_datetime:
            raise CancellationNotAllowed()

        self.reservation.cancel()
