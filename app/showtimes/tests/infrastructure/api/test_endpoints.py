from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.showtimes.application.create_showtime import CreateShowtimeParams
from app.showtimes.domain.exceptions import ShowtimeAlreadyExists
from app.showtimes.domain.seat import Seat, SeatStatus


class TestCreateShowtimeEndpoint:
    @pytest.fixture
    def mock_application(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.CreateShowtime") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.SqlModelShowtimeRepository") as mock:
            yield mock.return_value

    def test_returns_201_and_calls_action(
        self,
        client: TestClient,
        mock_application: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "room_id": "fbdd7b54-c561-4cbb-a55f-15853c60e600",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
            headers=superuser_token_headers,
        )

        mock_application.assert_called_once_with(repository=mock_repository)
        mock_application.return_value.execute.assert_called_once_with(
            params=CreateShowtimeParams(
                movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2022, 8, 10, 22, 0, 0, tzinfo=timezone.utc),
            )
        )

        assert response.status_code == 201

    def test_returns_400_when_showtime_already_exists(
        self,
        client: TestClient,
        mock_application: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_application.return_value.execute.side_effect = ShowtimeAlreadyExists

        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "room_id": "fbdd7b54-c561-4cbb-a55f-15853c60e600",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
            headers=superuser_token_headers,
        )

        mock_application.assert_called_once_with(repository=mock_repository)
        mock_application.return_value.execute.assert_called_once_with(
            params=CreateShowtimeParams(
                movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2022, 8, 10, 22, 0, 0, tzinfo=timezone.utc),
            )
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Showtime for movie already exists"}

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_application: Mock,
        mock_repository: Mock,
    ) -> None:
        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "room_id": "fbdd7b54-c561-4cbb-a55f-15853c60e600",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
        )

        mock_application.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_application: Mock,
        mock_repository: Mock,
        user_token_headers: dict[str, str],
    ) -> None:
        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "room_id": "fbdd7b54-c561-4cbb-a55f-15853c60e600",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
            headers=user_token_headers,
        )

        mock_application.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestDeleteShowtimeEndpoint:
    @pytest.fixture
    def mock_application(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.DeleteShowtime") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.SqlModelShowtimeRepository") as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(
        self,
        client: TestClient,
        mock_application: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_application.return_value.execute.return_value = None

        response = client.delete(
            "api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=superuser_token_headers,
        )

        mock_application.assert_called_once_with(repository=mock_repository)
        mock_application.return_value.execute.assert_called_once_with(
            showtime_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )

        assert response.status_code == 200

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_application: Mock,
        mock_repository: Mock,
    ) -> None:
        response = client.delete(
            "api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
        )

        mock_application.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_application: Mock,
        mock_repository: Mock,
        user_token_headers: dict[str, str],
    ) -> None:
        response = client.delete(
            "api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=user_token_headers,
        )

        mock_application.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestRetrieveSeatsEndpoint:
    @pytest.fixture
    def mock_application(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.RetrieveSeats") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.SqlModelShowtimeRepository") as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(
        self, client: TestClient, mock_application: Mock, mock_repository: Mock
    ) -> None:
        mock_application.return_value.execute.return_value = [
            Seat(id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"), row=1, number=1, status=SeatStatus.AVAILABLE),
            Seat(id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"), row=1, number=2, status=SeatStatus.RESERVED),
            Seat(id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e602"), row=2, number=1, status=SeatStatus.OCCUPIED),
        ]

        response = client.get("api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/seats/")

        mock_application.assert_called_once_with(repository=mock_repository)
        mock_application.return_value.execute.assert_called_once_with(
            showtime_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )

        assert response.status_code == 200
        assert response.json() == [
            {"id": "cbdd7b54-c561-4cbb-a55f-15853c60e600", "row": 1, "number": 1, "status": "available"},
            {"id": "cbdd7b54-c561-4cbb-a55f-15853c60e601", "row": 1, "number": 2, "status": "reserved"},
            {"id": "cbdd7b54-c561-4cbb-a55f-15853c60e602", "row": 2, "number": 1, "status": "occupied"},
        ]
