from sqlmodel import SQLModel

from app.showtimes.domain.seat import Seat


class SeatResponse(SQLModel):
    id: str
    row: int
    number: int
    status: str

    @classmethod
    def from_domain(cls, seat: Seat) -> "SeatResponse":
        return cls(id=seat.id, row=seat.row, number=seat.number, status=seat.status)

    @classmethod
    def from_domain_list(cls, seats: list[Seat]) -> list["SeatResponse"]:
        return [cls.from_domain(seat) for seat in seats]
