from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from sqlmodel import Session

from app.reservations.domain.reservation import ReservationStatus
from app.reservations.domain.seat import SeatStatus
from app.reservations.infrastructure.tasks import release_reservation_task
from app.reservations.tests.builders.sqlmodel_reservation_builder_test import SqlModelReservationBuilderTest
from app.reservations.tests.builders.sqlmodel_seat_builder_test import SqlModelSeatBuilderTest
from app.shared.domain.value_objects.id import Id


class TestReleaseReservationTask:
    @pytest.fixture
    def mock_release_reservation(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.tasks.ReleaseReservation") as mock:
            yield mock

    @pytest.fixture
    def mock_reservation_repository(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.tasks.SqlModelReservationRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_reservation_finder(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.tasks.SqlModelReservationFinder") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_db_session(self, session: Session) -> Generator[Session, None, None]:
        with patch("app.reservations.infrastructure.tasks.get_db_session") as mock:
            mock.return_value.__enter__.return_value = session
            yield session

    @pytest.mark.integration
    def test_integration(self, mock_db_session: Session) -> None:
        reservation_model = (
            SqlModelReservationBuilderTest(mock_db_session).with_status(ReservationStatus.PENDING).build()
        )
        seat_model = (
            SqlModelSeatBuilderTest(mock_db_session)
            .with_status(SeatStatus.RESERVED)
            .with_reservation_id(reservation_model.id)
            .build()
        )

        release_reservation_task(reservation_id=Id.from_uuid(reservation_model.id))

        assert seat_model.reservation_id is None
        assert seat_model.status == SeatStatus.AVAILABLE

    def test_calls_release_reservation(
        self, mock_release_reservation: Mock, mock_reservation_repository: Mock, mock_reservation_finder: Mock
    ) -> None:
        release_reservation_task(reservation_id="a116a257-a179-4d8f-9df9-a4e368475ed9")

        mock_release_reservation.assert_called_once_with(
            repository=mock_reservation_repository, finder=mock_reservation_finder
        )
        mock_release_reservation.return_value.execute.assert_called_once_with(
            reservation_id=Id("a116a257-a179-4d8f-9df9-a4e368475ed9")
        )
