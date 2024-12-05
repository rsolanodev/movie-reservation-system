from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest

from app.reservations.infrastructure.tasks import reservation_release_task
from app.shared.domain.value_objects.id import Id


class TestReleaseReservationTask:
    @pytest.fixture
    def mock_reservation_release(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.tasks.ReservationRelease") as mock:
            yield mock

    @pytest.fixture
    def mock_reservation_repository(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.tasks.SqlModelReservationRepository") as mock:
            yield mock.return_value

    def test_calls_reservation_release(self, mock_reservation_release: Mock, mock_reservation_repository: Mock) -> None:
        reservation_release_task(reservation_id="a116a257-a179-4d8f-9df9-a4e368475ed9")

        mock_reservation_release.assert_called_once_with(repository=mock_reservation_repository)
        mock_reservation_release.return_value.execute.assert_called_once_with(
            reservation_id=Id("a116a257-a179-4d8f-9df9-a4e368475ed9")
        )
