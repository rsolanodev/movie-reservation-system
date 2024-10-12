from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.showtimes.application.retrieve_seats import RetrieveSeats
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository
from app.showtimes.domain.seat import Seat, SeatStatus


class TestRetrieveSeats:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(ShowtimeRepository, instance=True)

    def test_retrieves_seats(self, mock_repository: Mock) -> None:
        mock_repository.retrive_seats.return_value = [
            Seat(id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"), row=1, number=1, status=SeatStatus.AVAILABLE),
            Seat(id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"), row=1, number=2, status=SeatStatus.RESERVED),
            Seat(id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e602"), row=2, number=1, status=SeatStatus.OCCUPIED),
        ]

        seats = RetrieveSeats(repository=mock_repository).execute(
            showtime_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600")
        )

        mock_repository.retrive_seats.assert_called_once_with(showtime_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"))

        assert seats == [
            Seat(id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"), row=1, number=1, status=SeatStatus.AVAILABLE),
            Seat(id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"), row=1, number=2, status=SeatStatus.RESERVED),
            Seat(id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e602"), row=2, number=1, status=SeatStatus.OCCUPIED),
        ]
