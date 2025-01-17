from collections.abc import Generator
from datetime import datetime
from typing import Any
from unittest.mock import Mock, create_autospec, patch

import pytest
from freezegun import freeze_time

from app.reservations.application.commands.cancel_expired_reservations import CancelExpiredReservations
from app.reservations.domain.collections.reservations import Reservations
from app.reservations.domain.finders.reservation_finder import ReservationFinder
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import ReservationStatus
from app.reservations.tests.builders.reservation_builder_test import ReservationBuilderTest
from app.settings import Settings
from app.shared.domain.value_objects.date_time import DateTime


@freeze_time("2025-01-10T00:30:00Z")
class TestCancelExpiredReservations:
    @pytest.fixture
    def mock_reservation_repository(self) -> Any:
        return create_autospec(spec=ReservationRepository, instance=True, spec_set=True)

    @pytest.fixture
    def mock_reservation_finder(self) -> Any:
        return create_autospec(spec=ReservationFinder, instance=True, spec_set=True)

    @pytest.fixture(autouse=True)
    def override_settings(self) -> Generator[None, None, None]:
        with patch(
            "app.reservations.application.commands.cancel_expired_reservations.settings",
            Settings(RESERVATION_EXPIRATION_MINUTES=10),
        ):
            yield

    def test_cancel_expired_reservations_when_created_at_is_older_than_10_minutes(
        self, mock_reservation_repository: Mock, mock_reservation_finder: Mock
    ) -> None:
        expected_reservation = (
            ReservationBuilderTest()
            .with_status(ReservationStatus.PENDING)
            .with_created_at(DateTime.from_datetime(datetime(2025, 1, 10, 00, 19, 59)))
            .build()
        )
        mock_reservation_finder.find_pending.return_value = Reservations([expected_reservation])

        CancelExpiredReservations(repository=mock_reservation_repository, finder=mock_reservation_finder).execute()

        mock_reservation_repository.cancel_reservations.assert_called_once_with(
            reservation_ids=[expected_reservation.id]
        )

    def test_does_not_cancel_expired_reservations_when_created_at_is_lower_than_10_minutes(
        self, mock_reservation_repository: Mock, mock_reservation_finder: Mock
    ) -> None:
        expected_reservation = (
            ReservationBuilderTest()
            .with_status(ReservationStatus.PENDING)
            .with_created_at(DateTime.from_datetime(datetime(2025, 1, 10, 00, 20, 0)))
            .build()
        )
        mock_reservation_finder.find_pending.return_value = Reservations([expected_reservation])

        CancelExpiredReservations(repository=mock_reservation_repository, finder=mock_reservation_finder).execute()

        mock_reservation_repository.cancel_reservations.assert_not_called()
