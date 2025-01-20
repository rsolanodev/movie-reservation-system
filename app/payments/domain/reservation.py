from dataclasses import dataclass
from enum import StrEnum

from app.shared.domain.value_objects.id import Id


class ReservationStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"


@dataclass
class Reservation:
    id: Id
    status: ReservationStatus

    def confirm(self) -> None:
        self.status = ReservationStatus.CONFIRMED
