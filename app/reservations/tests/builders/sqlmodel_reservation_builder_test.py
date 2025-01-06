import uuid

from sqlmodel import Session

from app.reservations.domain.reservation import ReservationStatus
from app.reservations.infrastructure.models import ReservationModel


class SqlModelReservationBuilderTest:
    def __init__(self, session: Session) -> None:
        self._session = session

        self.id: uuid.UUID = uuid.uuid4()
        self.user_id: uuid.UUID = uuid.uuid4()
        self.showtime_id: uuid.UUID = uuid.uuid4()
        self.has_paid: bool = False
        self.status: str = ReservationStatus.PENDING

    def with_id(self, id: uuid.UUID) -> "SqlModelReservationBuilderTest":
        self.id = id
        return self

    def with_user_id(self, user_id: uuid.UUID) -> "SqlModelReservationBuilderTest":
        self.user_id = user_id
        return self

    def with_showtime_id(self, showtime_id: uuid.UUID) -> "SqlModelReservationBuilderTest":
        self.showtime_id = showtime_id
        return self

    def with_has_paid(self, has_paid: bool) -> "SqlModelReservationBuilderTest":
        self.has_paid = has_paid
        return self

    def with_status(self, status: ReservationStatus) -> "SqlModelReservationBuilderTest":
        self.status = status
        return self

    def build(self) -> ReservationModel:
        reservation_model = ReservationModel(
            id=self.id,
            user_id=self.user_id,
            showtime_id=self.showtime_id,
            has_paid=self.has_paid,
            status=self.status,
        )
        self._session.add(reservation_model)
        return reservation_model
