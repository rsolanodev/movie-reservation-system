from uuid import UUID

from sqlmodel import SQLModel

from app.showtimes.domain.seat import Seat, SeatStatus


class SeatResponse(SQLModel):
    id: UUID
    row: int
    number: int
    status: SeatStatus

    @classmethod
    def from_domain(cls, seat: Seat) -> "SeatResponse":
        return cls(id=seat.id, row=seat.row, number=seat.number, status=seat.status)
