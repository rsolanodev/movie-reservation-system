from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.shared.domain.value_objects.id import Id
from app.showtimes.application.delete_showtime import DeleteShowtime
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository


class TestDeleteShowtime:
    @pytest.fixture
    def mock_showtime_repository(self) -> Any:
        return create_autospec(spec=ShowtimeRepository, instance=True, spec_set=True)

    def test_deletes_showtime(self, mock_showtime_repository: Mock) -> None:
        DeleteShowtime(repository=mock_showtime_repository).execute(
            showtime_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600")
        )

        mock_showtime_repository.delete.assert_called_once_with(
            showtime_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
        )
