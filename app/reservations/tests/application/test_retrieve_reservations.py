from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.reservations.application.retrieve_reservations import RetrieveReservations
from app.reservations.domain.movie_reservation import Movie, MovieReservation, ReservedSeat
from app.reservations.domain.repositories.reservation_repository import ReservationRepository


class TestRetrieveReservations:
    @pytest.fixture
    def mock_repostory(self) -> Any:
        return create_autospec(ReservationRepository, spec_set=True)

    def test_retrieve_reservations(self, mock_repostory: Mock) -> None:
        expected_movie_reservation = [
            MovieReservation(
                reservation_id=UUID("5661455d-de5a-47ba-b99f-f6d50fdfc00b"),
                show_datetime=datetime(2024, 1, 2, 22, 0, tzinfo=timezone.utc),
                movie=Movie(
                    id=UUID("d64a9a87-4484-46f9-8ec1-f1e1c9fe2880"),
                    title="Robot Salvaje",
                    poster_image="robot_salvaje.jpg",
                ),
                seats=[ReservedSeat(row=1, number=2)],
            ),
            MovieReservation(
                reservation_id=UUID("ffd7e9f4-bec7-4487-8f2f-d84b49d0bcee"),
                show_datetime=datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc),
                movie=Movie(
                    id=UUID("6c42605f-ac4a-405d-94f2-1f0ea3de5ddb"),
                    title="La Sustancia",
                    poster_image="la_sustancia.jpg",
                ),
                seats=[ReservedSeat(row=3, number=4)],
            ),
        ]
        mock_repostory.find_by_user_id.return_value = expected_movie_reservation

        movie_reservations = RetrieveReservations(repository=mock_repostory).execute(
            user_id=UUID("123e4567-e89b-12d3-a456-426614174000")
        )

        mock_repostory.find_by_user_id.assert_called_once_with(user_id=UUID("123e4567-e89b-12d3-a456-426614174000"))

        assert movie_reservations == expected_movie_reservation
