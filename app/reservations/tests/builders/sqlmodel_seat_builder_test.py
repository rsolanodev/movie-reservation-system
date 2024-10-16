import uuid

from sqlmodel import Session

from app.reservations.domain.seat import SeatStatus
from app.reservations.infrastructure.models import SeatModel


class SqlModelSeatBuilderTest:
    def __init__(self, session: Session) -> None:
        self._session = session

        self.id: uuid.UUID = uuid.uuid4()
        self.row: int = 1
        self.number: int = 1
        self.status: SeatStatus = SeatStatus.AVAILABLE
        self.showtime_id: uuid.UUID = uuid.uuid4()
        self.reservation_id: uuid.UUID | None = None

    def with_id(self, id: uuid.UUID) -> "SqlModelSeatBuilderTest":
        self.id = id
        return self

    def with_row(self, row: int) -> "SqlModelSeatBuilderTest":
        self.row = row
        return self

    def with_number(self, number: int) -> "SqlModelSeatBuilderTest":
        self.number = number
        return self

    def with_status(self, status: SeatStatus) -> "SqlModelSeatBuilderTest":
        self.status = status
        return self

    def with_showtime_id(self, showtime_id: uuid.UUID) -> "SqlModelSeatBuilderTest":
        self.showtime_id = showtime_id
        return self

    def with_reservation_id(self, reservation_id: uuid.UUID) -> "SqlModelSeatBuilderTest":
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
