from datetime import datetime, timezone
from typing import Any
from unittest.mock import ANY, Mock, create_autospec
from uuid import UUID

import pytest

from app.showtimes.application.create_showtime import CreateShowtime, CreateShowtimeParams
from app.showtimes.domain.exceptions import ShowtimeAlreadyExists
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository
from app.showtimes.domain.showtime import Showtime


class TestCreateShowtime:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(ShowtimeRepository, instance=True)

    def test_creates_showtime(self, mock_repository: Mock) -> None:
        mock_repository.exists.return_value = False

        CreateShowtime(repository=mock_repository).execute(
            params=CreateShowtimeParams(
                movie_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2023, 4, 2, 20, 0, tzinfo=timezone.utc),
            )
        )

        mock_repository.exists.assert_called_once_with(
            showtime=Showtime(
                id=ANY,
                movie_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2023, 4, 2, 20, 0, tzinfo=timezone.utc),
            )
        )
        mock_repository.create.assert_called_once_with(
            showtime=Showtime(
                id=ANY,
                movie_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2023, 4, 2, 20, 0, tzinfo=timezone.utc),
            )
        )

    def test_does_not_create_showtime_when_exists(self, mock_repository: Mock) -> None:
        mock_repository.exists.return_value = True

        with pytest.raises(ShowtimeAlreadyExists):
            CreateShowtime(repository=mock_repository).execute(
                params=CreateShowtimeParams(
                    movie_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                    room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                    show_datetime=datetime(2023, 4, 2, 20, 0, tzinfo=timezone.utc),
                )
            )

        mock_repository.exists.assert_called_once_with(
            showtime=Showtime(
                id=ANY,
                movie_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2023, 4, 2, 20, 0, tzinfo=timezone.utc),
            )
        )
        mock_repository.create.assert_not_called()
