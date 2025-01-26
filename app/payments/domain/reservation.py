from dataclasses import dataclass
from typing import Self

from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus


@dataclass
class Reservation:
    id: Id
    status: ReservationStatus

    @classmethod
    def update_status(cls, id: str, status: ReservationStatus) -> Self:
        return cls(id=Id(id), status=status)

    def confirm(self) -> None:
        self.status = ReservationStatus.CONFIRMED
