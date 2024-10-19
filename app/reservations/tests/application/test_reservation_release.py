from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.reservations.application.reservation_release import ReservationRelease
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.tests.builders.reservation_builder_test import ReservationBuilderTest


class TestReservationRelease:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(ReservationRepository, instance=True)

    def test_releases_reservation_when_has_been_paid(self, mock_repository: Mock) -> None:
        expected_reservation = ReservationBuilderTest().with_has_paid(True).build()
        mock_repository.get.return_value = expected_reservation

        ReservationRelease(repository=mock_repository).execute(reservation_id=expected_reservation.id)

        mock_repository.release.assert_called_once_with(expected_reservation.id)

    def test_does_not_release_reservation_when_has_not_been_paid(self, mock_repository: Mock) -> None:
        expected_reservation = ReservationBuilderTest().with_has_paid(False).build()
        mock_repository.get.return_value = expected_reservation

        ReservationRelease(repository=mock_repository).execute(reservation_id=expected_reservation.id)

        mock_repository.release.assert_not_called()
