import uuid

from app.reservations.domain.seat import Seat, SeatStatus
from app.reservations.domain.value_objects.id import ID


class SeatBuilderTest:
    def __init__(self) -> None:
        self.id: ID = ID.from_uuid(uuid.uuid4())
        self.row: int = 1
        self.number: int = 1
        self.status: SeatStatus = SeatStatus.AVAILABLE

    def with_id(self, id: ID) -> "SeatBuilderTest":
        self.id = id
        return self

    def with_row(self, row: int) -> "SeatBuilderTest":
        self.row = row
        return self

    def with_number(self, number: int) -> "SeatBuilderTest":
        self.number = number
        return self

    def with_status(self, status: SeatStatus) -> "SeatBuilderTest":
        self.status = status
        return self

    def build(self) -> Seat:
        return Seat(id=self.id, row=self.row, number=self.number, status=self.status)
