from collections.abc import Generator
from unittest.mock import Mock, patch
from uuid import UUID

import pytest

from app.reservations.infrastructure.tasks import reservation_release_task


class TestReleaseReservationTask:
    @pytest.fixture
    def mock_application(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.tasks.ReservationRelease") as mock:
            yield mock.return_value

    def test_calls_application(self, mock_application: Mock) -> None:
        reservation_release_task(reservation_id="a116a257-a179-4d8f-9df9-a4e368475ed9")

        mock_application.execute.assert_called_once_with(reservation_id=UUID("a116a257-a179-4d8f-9df9-a4e368475ed9"))
