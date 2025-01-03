from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.reservations.application.release_reservation import ReleaseReservation
from app.reservations.domain.finders.reservation_finder import ReservationFinder
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.tests.builders.reservation_builder_test import ReservationBuilderTest


class TestReservationRelease:
    @pytest.fixture
    def mock_reservation_repository(self) -> Any:
        return create_autospec(spec=ReservationRepository, instance=True, spec_set=True)

    @pytest.fixture
    def mock_reservation_finder(self) -> Any:
        return create_autospec(spec=ReservationFinder, instance=True, spec_set=True)

    def test_releases_reservation_when_has_not_been_paid(
        self, mock_reservation_repository: Mock, mock_reservation_finder: Mock
    ) -> None:
        expected_reservation = ReservationBuilderTest().with_has_paid(False).build()
        mock_reservation_finder.find_reservation.return_value = expected_reservation

        ReleaseReservation(repository=mock_reservation_repository, finder=mock_reservation_finder).execute(
            reservation_id=expected_reservation.id
        )

        mock_reservation_repository.release.assert_called_once_with(expected_reservation.id)

    def test_does_not_release_reservation_when_has_been_paid(
        self, mock_reservation_repository: Mock, mock_reservation_finder: Mock
    ) -> None:
        expected_reservation = ReservationBuilderTest().with_has_paid(True).build()
        mock_reservation_finder.find_reservation.return_value = expected_reservation

        ReleaseReservation(repository=mock_reservation_repository, finder=mock_reservation_finder).execute(
            reservation_id=expected_reservation.id
        )

        mock_reservation_repository.release.assert_not_called()
