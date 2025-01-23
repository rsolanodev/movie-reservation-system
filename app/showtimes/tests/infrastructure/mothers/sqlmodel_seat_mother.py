from typing import Self
from uuid import UUID

from sqlmodel import Session

from app.reservations.infrastructure.models import SeatModel
from app.shared.domain.value_objects.seat_status import SeatStatus


class SqlModelSeatMother:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._seat_model = SeatModel(
            id=UUID("b1b008b4-f1b2-41a2-8388-9f33fc5aec64"),
            showtime_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
            status=SeatStatus.AVAILABLE.value,
            row=1,
            number=1,
        )

    def with_id(self, id: UUID) -> Self:
        self._seat_model.id = id
        return self

    def with_showtime_id(self, showtime_id: UUID) -> Self:
        self._seat_model.showtime_id = showtime_id
        return self

    def with_status(self, status: SeatStatus) -> Self:
        self._seat_model.status = status.value
        return self

    def occupied(self) -> Self:
        self._seat_model.status = SeatStatus.OCCUPIED.value
        return self

    def reserved(self) -> Self:
        self._seat_model.status = SeatStatus.RESERVED.value
        return self

    def available(self) -> Self:
        self._seat_model.status = SeatStatus.AVAILABLE.value
        return self

    def with_row(self, row: int) -> Self:
        self._seat_model.row = row
        return self

    def with_number(self, number: int) -> Self:
        self._seat_model.number = number
        return self

    def create(self) -> SeatModel:
        self._session.add(self._seat_model)
        return self._seat_model
