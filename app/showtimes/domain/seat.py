from dataclasses import dataclass
from enum import StrEnum

from app.shared.domain.value_objects.id import Id


class SeatStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"


@dataclass
class Seat:
    id: Id
    row: int
    number: int
    status: SeatStatus
