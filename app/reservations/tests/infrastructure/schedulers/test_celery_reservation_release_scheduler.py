from collections.abc import Generator
from datetime import timedelta
from unittest.mock import Mock, patch

import pytest

from app.reservations.infrastructure.schedulers.celery_reservation_release_scheduler import (
    CeleryReservationReleaseScheduler,
)
from app.shared.domain.value_objects.id import Id


class TestCeleryReservationReleaseScheduler:
    @pytest.fixture
    def mock_release_reservation_task(self) -> Generator[Mock, None, None]:
        with patch(
            "app.reservations.infrastructure.schedulers.celery_reservation_release_scheduler.release_reservation_task"
        ) as mock:
            yield mock

    def test_schedules_release_reservation_task(self, mock_release_reservation_task: Mock) -> None:
        CeleryReservationReleaseScheduler().schedule(
            reservation_id=Id("d9326dd9-2909-42d8-8350-f01a378c0f7c"), delay=timedelta(minutes=15)
        )

        mock_release_reservation_task.apply_async.assert_called_once_with(
            args=("d9326dd9-2909-42d8-8350-f01a378c0f7c",), countdown=900.0
        )
