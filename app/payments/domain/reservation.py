from dataclasses import dataclass

from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus


@dataclass
class Reservation:
    id: Id
    status: ReservationStatus

    def confirm(self) -> None:
        self.status = ReservationStatus.CONFIRMED
