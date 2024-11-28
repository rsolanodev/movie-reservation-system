from collections.abc import Generator
from datetime import timedelta
from unittest.mock import Mock, patch

import pytest

from app.reservations.infrastructure.schedulers.celery_reservation_release_scheduler import (
    CeleryReservationReleaseScheduler,
)
from app.shared.domain.value_objects.id import ID


class TestCeleryReservationReleaseScheduler:
    @pytest.fixture
    def mock_reservation_release_task(self) -> Generator[Mock, None, None]:
        with patch(
            "app.reservations.infrastructure.schedulers.celery_reservation_release_scheduler.reservation_release_task"
        ) as mock:
            yield mock

    def test_schedules_reservation_release_task(self, mock_reservation_release_task: Mock) -> None:
        CeleryReservationReleaseScheduler().schedule(
            reservation_id=ID("d9326dd9-2909-42d8-8350-f01a378c0f7c"), delay=timedelta(minutes=15)
        )

        mock_reservation_release_task.apply_async.assert_called_once_with(
            args=("d9326dd9-2909-42d8-8350-f01a378c0f7c",), countdown=900.0
        )
