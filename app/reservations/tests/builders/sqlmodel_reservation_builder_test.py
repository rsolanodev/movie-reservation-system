import uuid
from datetime import datetime

from sqlmodel import Session

from app.reservations.domain.reservation import ReservationStatus
from app.reservations.infrastructure.models import ReservationModel


class SqlModelReservationBuilderTest:
    def __init__(self, session: Session) -> None:
        self._session = session

        self.id: uuid.UUID = uuid.uuid4()
        self.user_id: uuid.UUID = uuid.uuid4()
        self.showtime_id: uuid.UUID = uuid.uuid4()
        self.status: str = ReservationStatus.PENDING
        self.created_at: datetime = datetime.now()

    def with_id(self, id: uuid.UUID) -> "SqlModelReservationBuilderTest":
        self.id = id
        return self

    def with_user_id(self, user_id: uuid.UUID) -> "SqlModelReservationBuilderTest":
        self.user_id = user_id
        return self

    def with_showtime_id(self, showtime_id: uuid.UUID) -> "SqlModelReservationBuilderTest":
        self.showtime_id = showtime_id
        return self

    def with_status(self, status: ReservationStatus) -> "SqlModelReservationBuilderTest":
        self.status = status
        return self

    def with_created_at(self, created_at: datetime) -> "SqlModelReservationBuilderTest":
        self.created_at = created_at
        return self

    def build(self) -> ReservationModel:
        reservation_model = ReservationModel(
            id=self.id,
            user_id=self.user_id,
            showtime_id=self.showtime_id,
            status=self.status,
            created_at=self.created_at,
        )
        self._session.add(reservation_model)
        return reservation_model
