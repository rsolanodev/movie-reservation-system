from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.showtimes.actions.delete_showtime import DeleteShowtime
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository


class TestDeleteShowtime:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(ShowtimeRepository, instance=True)

    def test_creates_showtime(self, mock_repository: Mock) -> None:
        DeleteShowtime(repository=mock_repository).execute(
            showtime_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600")
        )

        mock_repository.delete.assert_called_once_with(
            showtime_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600")
        )
