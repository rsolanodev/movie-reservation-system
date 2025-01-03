from app.reservations.domain.seat import Seat, SeatStatus


class Seats(list[Seat]):
    def are_available(self) -> bool:
        return all(seat.status == SeatStatus.AVAILABLE for seat in self)
