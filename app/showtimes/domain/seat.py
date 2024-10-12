from dataclasses import dataclass
from uuid import UUID

from app.reservations.infrastructure.models import SeatStatus


@dataclass
class Seat:
    id: UUID
    row: int
    number: int
    status: SeatStatus
