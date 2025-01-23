from datetime import datetime
from typing import Any
from unittest.mock import Mock, create_autospec

import pytest
from freezegun import freeze_time

from app.reservations.application.commands.cancel_reservation import CancelReservation, CancelReservationParams
from app.reservations.domain.exceptions import CancellationNotAllowed, ReservationNotFound, UnauthorizedCancellation
from app.reservations.domain.finders.reservation_finder import ReservationFinder
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import CancellableReservation
from app.reservations.tests.domain.mothers.reservation_mother import ReservationMother
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id


@freeze_time("2025-01-22T22:00:00Z")
class TestCancelReservation:
    @pytest.fixture
    def mock_reservation_repository(self) -> Any:
        return create_autospec(spec=ReservationRepository, instance=True, spec_set=True)

    @pytest.fixture
    def mock_reservation_finder(self) -> Any:
        return create_autospec(spec=ReservationFinder, instance=True, spec_set=True)

    def test_cancel_reservation(self, mock_reservation_repository: Mock, mock_reservation_finder: Mock) -> None:
        reservation = ReservationMother().create()
        mock_reservation_finder.find_cancellable_reservation.return_value = CancellableReservation(
            reservation=reservation, show_datetime=DateTime.from_datetime(datetime(2025, 1, 22, 23, 0, 0))
        )

        CancelReservation(finder=mock_reservation_finder, repository=mock_reservation_repository).execute(
            CancelReservationParams(reservation_id=reservation.id, user_id=reservation.user_id)
        )

        mock_reservation_finder.find_cancellable_reservation.assert_called_once_with(reservation_id=reservation.id)
        mock_reservation_repository.save.assert_called_once_with(reservation=ReservationMother().cancelled().create())

    def test_raise_exception_when_reservation_not_found(
        self, mock_reservation_finder: Mock, mock_reservation_repository: Mock
    ) -> None:
        mock_reservation_finder.find_cancellable_reservation.return_value = None

        with pytest.raises(ReservationNotFound):
            CancelReservation(finder=mock_reservation_finder, repository=mock_reservation_repository).execute(
                CancelReservationParams(
                    reservation_id=Id("434d5682-0a19-499e-a72a-c08f47b43e09"),
                    user_id=Id("6ae2c28b-fed8-4699-872b-6b889ea27bff"),
                )
            )

        mock_reservation_finder.find_cancellable_reservation.assert_called_once_with(
            reservation_id=Id("434d5682-0a19-499e-a72a-c08f47b43e09")
        )
        mock_reservation_repository.save.assert_not_called()

    def test_raise_exception_when_user_is_not_the_owner_of_the_reservation(
        self, mock_reservation_finder: Mock, mock_reservation_repository: Mock
    ) -> None:
        reservation = ReservationMother().create()
        mock_reservation_finder.find_cancellable_reservation.return_value = CancellableReservation(
            reservation=reservation, show_datetime=DateTime.from_datetime(datetime(2025, 1, 22, 23, 0, 0))
        )

        with pytest.raises(UnauthorizedCancellation):
            CancelReservation(finder=mock_reservation_finder, repository=mock_reservation_repository).execute(
                CancelReservationParams(
                    reservation_id=reservation.id,
                    user_id=Id("6ae2c28b-fed8-4699-872b-6b889ea27bee"),
                )
            )

        mock_reservation_finder.find_cancellable_reservation.assert_called_once_with(reservation_id=reservation.id)
        mock_reservation_repository.save.assert_not_called()

    def test_raise_exception_when_showtime_has_started(
        self, mock_reservation_finder: Mock, mock_reservation_repository: Mock
    ) -> None:
        reservation = ReservationMother().create()
        mock_reservation_finder.find_cancellable_reservation.return_value = CancellableReservation(
            reservation=reservation, show_datetime=DateTime.from_datetime(datetime(2025, 1, 22, 22, 0, 0))
        )

        with pytest.raises(CancellationNotAllowed):
            CancelReservation(finder=mock_reservation_finder, repository=mock_reservation_repository).execute(
                CancelReservationParams(reservation_id=reservation.id, user_id=reservation.user_id)
            )

        mock_reservation_finder.find_cancellable_reservation.assert_called_once_with(reservation_id=reservation.id)
        mock_reservation_repository.save.assert_not_called()
