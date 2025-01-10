from collections.abc import Generator
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from freezegun import freeze_time
from sqlmodel import Session

from app.reservations.application.jobs.cancel_expired_reservations_job import cancel_expired_reservations_job
from app.reservations.domain.reservation import ReservationStatus
from app.reservations.domain.seat import SeatStatus
from app.reservations.tests.builders.sqlmodel_reservation_builder_test import SqlModelReservationBuilderTest
from app.reservations.tests.builders.sqlmodel_seat_builder_test import SqlModelSeatBuilderTest
from app.settings import Settings


class TestCancelExpiredReservationsJob:
    @pytest.fixture
    def mock_cancel_expired_reservations(self) -> Generator[Mock, None, None]:
        with patch(
            "app.reservations.application.jobs.cancel_expired_reservations_job.CancelExpiredReservations"
        ) as mock:
            yield mock

    @pytest.fixture
    def mock_reservation_repository(self) -> Generator[Mock, None, None]:
        with patch(
            "app.reservations.application.jobs.cancel_expired_reservations_job.SqlModelReservationRepository"
        ) as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_reservation_finder(self) -> Generator[Mock, None, None]:
        with patch(
            "app.reservations.application.jobs.cancel_expired_reservations_job.SqlModelReservationFinder"
        ) as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_db_session(self, session: Session) -> Generator[Session, None, None]:
        with patch("app.reservations.application.jobs.cancel_expired_reservations_job.get_session") as mock:
            mock.return_value.__enter__.return_value = session
            yield session

    @pytest.fixture(autouse=True)
    def override_settings(self) -> Generator[None, None, None]:
        with patch(
            "app.shared.infrastructure.storages.s3_storage.get_settings",
            return_value=Settings(RESERVATION_EXPIRATION_MINUTES=10),
        ):
            yield

    @pytest.mark.integration
    @freeze_time("2025-01-10T00:30:00Z")
    def test_integration(self, mock_db_session: Session) -> None:
        reservation_model = (
            SqlModelReservationBuilderTest(mock_db_session)
            .with_status(ReservationStatus.PENDING)
            .with_created_at(datetime(2025, 1, 10, 00, 19, 59))
            .build()
        )
        seat_model = (
            SqlModelSeatBuilderTest(mock_db_session)
            .with_status(SeatStatus.RESERVED)
            .with_reservation_id(reservation_model.id)
            .build()
        )

        cancel_expired_reservations_job()

        assert reservation_model.status == ReservationStatus.CANCELLED
        assert seat_model.status == SeatStatus.AVAILABLE
        assert seat_model.reservation_id is None

    def test_calls_cancel_expired_reservations(
        self, mock_cancel_expired_reservations: Mock, mock_reservation_repository: Mock, mock_reservation_finder: Mock
    ) -> None:
        cancel_expired_reservations_job()

        mock_cancel_expired_reservations.assert_called_once_with(
            repository=mock_reservation_repository, finder=mock_reservation_finder
        )
        mock_cancel_expired_reservations.return_value.execute.assert_called_once()
