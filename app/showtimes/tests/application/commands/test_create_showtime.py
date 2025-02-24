from datetime import datetime
from typing import Any
from unittest.mock import ANY, Mock, create_autospec

import pytest

from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.showtimes.application.commands.create_showtime import CreateShowtime, CreateShowtimeParams
from app.showtimes.domain.exceptions import ShowtimeAlreadyExists
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository
from app.showtimes.domain.showtime import Showtime


class TestCreateShowtime:
    @pytest.fixture
    def mock_showtime_repository(self) -> Any:
        return create_autospec(spec=ShowtimeRepository, instance=True, spec_set=True)

    def test_creates_showtime(self, mock_showtime_repository: Mock) -> None:
        mock_showtime_repository.exists.return_value = False

        CreateShowtime(repository=mock_showtime_repository).execute(
            params=CreateShowtimeParams(
                movie_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                room_id=Id("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=DateTime.from_datetime(datetime(2023, 4, 2, 20, 0)),
            )
        )

        mock_showtime_repository.exists.assert_called_once_with(
            showtime=Showtime(
                id=ANY,
                movie_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                room_id=Id("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=DateTime.from_datetime(datetime(2023, 4, 2, 20, 0)),
            )
        )
        mock_showtime_repository.create.assert_called_once_with(
            showtime=Showtime(
                id=ANY,
                movie_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                room_id=Id("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=DateTime.from_datetime(datetime(2023, 4, 2, 20, 0)),
            )
        )

    def test_does_not_create_showtime_when_exists(self, mock_showtime_repository: Mock) -> None:
        mock_showtime_repository.exists.return_value = True

        with pytest.raises(ShowtimeAlreadyExists):
            CreateShowtime(repository=mock_showtime_repository).execute(
                params=CreateShowtimeParams(
                    movie_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                    room_id=Id("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                    show_datetime=DateTime.from_datetime(datetime(2023, 4, 2, 20, 0)),
                )
            )

        mock_showtime_repository.exists.assert_called_once_with(
            showtime=Showtime(
                id=ANY,
                movie_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                room_id=Id("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=DateTime.from_datetime(datetime(2023, 4, 2, 20, 0)),
            )
        )
        mock_showtime_repository.create.assert_not_called()
