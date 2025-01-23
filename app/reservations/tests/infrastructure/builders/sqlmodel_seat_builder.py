import uuid
from typing import Self

from sqlmodel import Session

from app.reservations.domain.seat import SeatStatus
from app.reservations.infrastructure.models import SeatModel


class SqlModelSeatBuilder:
    def __init__(self, session: Session) -> None:
        self._session = session

        self.id: uuid.UUID = uuid.uuid4()
        self.row: int = 1
        self.number: int = 1
        self.status: str = SeatStatus.AVAILABLE.value
        self.showtime_id: uuid.UUID = uuid.uuid4()
        self.reservation_id: uuid.UUID | None = None

    def with_id(self, id: uuid.UUID) -> Self:
        self.id = id
        return self

    def with_row(self, row: int) -> Self:
        self.row = row
        return self

    def with_number(self, number: int) -> Self:
        self.number = number
        return self

    def with_status(self, status: str) -> Self:
        self.status = status
        return self

    def available(self) -> Self:
        self.status = SeatStatus.AVAILABLE.value
        return self

    def reserved(self) -> Self:
        self.status = SeatStatus.RESERVED.value
        return self

    def occupied(self) -> Self:
        self.status = SeatStatus.OCCUPIED.value
        return self

    def with_showtime_id(self, showtime_id: uuid.UUID) -> Self:
        self.showtime_id = showtime_id
        return self

    def with_reservation_id(self, reservation_id: uuid.UUID) -> Self:
        self.reservation_id = reservation_id
        return self

    def build(self) -> SeatModel:
        seat_model = SeatModel(
            id=self.id,
            row=self.row,
            number=self.number,
            status=self.status,
            showtime_id=self.showtime_id,
            reservation_id=self.reservation_id,
        )
        self._session.add(seat_model)
        return seat_model
