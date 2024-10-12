import uuid

from sqlmodel import Session

from app.reservations.infrastructure.models import SeatModel
from app.showtimes.domain.seat import SeatStatus


class SeatModelFactory:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        row: int,
        number: int,
        status: SeatStatus = SeatStatus.AVAILABLE,
        showtime_id: uuid.UUID | None = None,
        id: uuid.UUID | None = None,
    ) -> SeatModel:
        seat_model = SeatModel(
            id=id or uuid.uuid4(), showtime_id=showtime_id or uuid.uuid4(), row=row, number=number, status=status
        )
        self._session.add(seat_model)
        return seat_model
