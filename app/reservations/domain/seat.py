import uuid
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
    status: str

    @classmethod
    def create(cls, row: int, number: int, status: str) -> "Seat":
        return cls(id=Id.from_uuid(uuid.uuid4()), row=row, number=number, status=status)
