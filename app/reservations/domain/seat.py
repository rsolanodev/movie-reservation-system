import uuid
from dataclasses import dataclass
from enum import StrEnum


class SeatStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"


@dataclass
class Seat:
    id: uuid.UUID
    row: int
    number: int
    status: str

    @classmethod
    def create(cls, row: int, number: int, status: str) -> "Seat":
        return cls(id=uuid.uuid4(), row=row, number=number, status=status)
