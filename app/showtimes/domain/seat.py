from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class SeatStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"


@dataclass
class Seat:
    id: UUID
    row: int
    number: int
    status: SeatStatus
