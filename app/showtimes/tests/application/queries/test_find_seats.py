from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.shared.domain.value_objects.id import Id
from app.showtimes.application.queries.find_seats import FindSeats
from app.showtimes.domain.finders.seat_finder import SeatFinder
from app.showtimes.domain.seat import Seat, SeatStatus


class TestFindSeats:
    @pytest.fixture
    def mock_seat_finder(self) -> Any:
        return create_autospec(spec=SeatFinder, instance=True, spec_set=True)

    def test_finds_seats(self, mock_seat_finder: Mock) -> None:
        mock_seat_finder.find_seats_by_showtime_id.return_value = [
            Seat(id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"), row=1, number=1, status=SeatStatus.AVAILABLE),
            Seat(id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e601"), row=1, number=2, status=SeatStatus.RESERVED),
            Seat(id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e602"), row=2, number=1, status=SeatStatus.OCCUPIED),
        ]

        seats = FindSeats(finder=mock_seat_finder).execute(showtime_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"))

        mock_seat_finder.find_seats_by_showtime_id.assert_called_once_with(
            showtime_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600")
        )

        assert seats == [
            Seat(id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"), row=1, number=1, status=SeatStatus.AVAILABLE),
            Seat(id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e601"), row=1, number=2, status=SeatStatus.RESERVED),
            Seat(id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e602"), row=2, number=1, status=SeatStatus.OCCUPIED),
        ]
