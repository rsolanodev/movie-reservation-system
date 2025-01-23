from dataclasses import dataclass

from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.seat_status import SeatStatus


@dataclass
class Seat:
    id: Id
    row: int
    number: int
    status: SeatStatus
