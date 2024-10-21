from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.reservations.application.create_reservation import CreateReservationParams
from app.reservations.domain.exceptions import SeatsNotAvailable
from app.reservations.domain.movie_reservation import Movie, MovieReservation, ReservedSeat
from app.users.infrastructure.models import UserModel


class TestCreateReservationEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.CreateReservation") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.SqlModelReservationRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_reservation_release_scheduler(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.CeleryReservationReleaseScheduler") as mock:
            yield mock.return_value

    def test_returns_201_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        mock_reservation_release_scheduler: Mock,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
        response = client.post(
            "api/v1/reservations/",
            json={
                "showtime_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "seat_ids": ["b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1"],
            },
            headers=user_token_headers,
        )

        mock_action.assert_called_once_with(
            repository=mock_repository,
            reservation_release_scheduler=mock_reservation_release_scheduler,
        )
        mock_action.return_value.execute.assert_called_once_with(
            params=CreateReservationParams(
                showtime_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                seat_ids=[UUID("b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1")],
                user_id=user.id,
            )
        )

        assert response.status_code == 201

    def test_returns_400_when_seats_not_available(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        mock_reservation_release_scheduler: Mock,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
        mock_action.return_value.execute.side_effect = SeatsNotAvailable

        response = client.post(
            "api/v1/reservations/",
            json={
                "showtime_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "seat_ids": ["b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1"],
            },
            headers=user_token_headers,
        )

        mock_action.assert_called_once_with(
            repository=mock_repository,
            reservation_release_scheduler=mock_reservation_release_scheduler,
        )
        mock_action.return_value.execute.assert_called_once_with(
            params=CreateReservationParams(
                showtime_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                seat_ids=[UUID("b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1")],
                user_id=user.id,
            )
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Seats not available"}

    def test_returns_401_when_user_is_not_authenticated(
        self, client: TestClient, mock_action: Mock, mock_repository: Mock
    ) -> None:
        response = client.post(
            "api/v1/reservations/",
            json={
                "showtime_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "seat_ids": ["b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1"],
            },
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


class TestRetrieveReservationsEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.RetrieveReservations") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.SqlModelReservationRepository") as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
        mock_action.return_value.execute.return_value = [
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

        response = client.get("api/v1/reservations/", headers=user_token_headers)

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(user_id=user.id)

        assert response.status_code == 200
        assert response.json() == [
            {
                "reservation_id": "5661455d-de5a-47ba-b99f-f6d50fdfc00b",
                "show_datetime": "2024-01-02T22:00:00Z",
                "movie": {
                    "id": "d64a9a87-4484-46f9-8ec1-f1e1c9fe2880",
                    "title": "Robot Salvaje",
                    "poster_image": "robot_salvaje.jpg",
                },
                "seats": [{"row": 1, "number": 2}],
            },
            {
                "reservation_id": "ffd7e9f4-bec7-4487-8f2f-d84b49d0bcee",
                "show_datetime": "2024-01-01T20:00:00Z",
                "movie": {
                    "id": "6c42605f-ac4a-405d-94f2-1f0ea3de5ddb",
                    "title": "La Sustancia",
                    "poster_image": "la_sustancia.jpg",
                },
                "seats": [{"row": 3, "number": 4}],
            },
        ]

    def test_returns_401_when_user_is_not_authenticated(
        self, client: TestClient, mock_action: Mock, mock_repository: Mock
    ) -> None:
        response = client.get("api/v1/reservations/")

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}
