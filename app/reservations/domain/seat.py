import uuid
from dataclasses import dataclass

from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.seat_status import SeatStatus


@dataclass
class Seat:
    id: Id
    row: int
    number: int
    status: SeatStatus

    @classmethod
    def create(cls, row: int, number: int, status: SeatStatus) -> "Seat":
        return cls(id=Id.from_uuid(uuid.uuid4()), row=row, number=number, status=status)
