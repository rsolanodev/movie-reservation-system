import uuid
from dataclasses import dataclass
from enum import StrEnum

from app.reservations.domain.value_objects.id import ID


class SeatStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"


@dataclass
class Seat:
    id: ID
    row: int
    number: int
    status: str

    @classmethod
    def create(cls, row: int, number: int, status: str) -> "Seat":
        return cls(id=ID.from_uuid(uuid.uuid4()), row=row, number=number, status=status)
