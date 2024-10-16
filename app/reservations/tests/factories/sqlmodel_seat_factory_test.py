from sqlmodel import Session

from app.reservations.domain.seat import SeatStatus
from app.reservations.infrastructure.models import SeatModel
from app.reservations.tests.builders.sqlmodel_seat_builder_test import SqlModelSeatBuilderTest


class SqlModelSeatFactoryTest:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_available(self) -> SeatModel:
        return SqlModelSeatBuilderTest(self.session).with_status(SeatStatus.AVAILABLE).build()
