import uuid
from dataclasses import dataclass
from enum import StrEnum

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.exceptions import CancellationNotAllowed, UnauthorizedCancellation
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
    seats: Seats
    created_at: DateTime

    provider_payment_id: str | None = None

    @classmethod
    def create(cls, user_id: Id, showtime_id: Id, seats: Seats | None = None) -> "Reservation":
        return cls(
            id=Id.from_uuid(uuid.uuid4()),
            user_id=user_id,
            showtime_id=showtime_id,
            status=ReservationStatus.PENDING,
            seats=seats or Seats([]),
            created_at=DateTime.now(),
        )

    def add_seats(self, seats: Seats) -> None:
        self.seats.extend(seats)

    def is_confirmed(self) -> bool:
        return self.status == ReservationStatus.CONFIRMED

    def cancel(self) -> None:
        self.status = ReservationStatus.CANCELLED

    def assign_payment_id(self, provider_payment_id: str) -> None:
        self.provider_payment_id = provider_payment_id


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
