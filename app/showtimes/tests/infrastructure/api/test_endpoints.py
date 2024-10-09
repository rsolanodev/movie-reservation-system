from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.showtimes.application.create_showtime import CreateShowtimeParams
from app.showtimes.domain.exceptions import ShowtimeAlreadyExistsException


class TestCreateShowtimeEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.CreateShowtime") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.SqlModelShowtimeRepository") as mock:
            yield mock.return_value

    def test_returns_201_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=CreateShowtimeParams(
                movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                show_datetime=datetime(2022, 8, 10, 22, 0, 0, tzinfo=timezone.utc),
            )
        )

        assert response.status_code == 201

    def test_returns_400_when_showtime_already_exists(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.side_effect = ShowtimeAlreadyExistsException

        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=CreateShowtimeParams(
                movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                show_datetime=datetime(2022, 8, 10, 22, 0, 0, tzinfo=timezone.utc),
            )
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Showtime for movie already exists"}

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        user_token_headers: dict[str, str],
    ) -> None:
        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
            headers=user_token_headers,
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestDeleteShowtimeEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.DeleteShowtime") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.SqlModelShowtimeRepository") as mock:
            yield mock.return_value

    def test_returns_200_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_action.return_value.execute.return_value = None

        response = client.delete(
            "api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=superuser_token_headers,
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            showtime_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )

        assert response.status_code == 200

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        response = client.delete(
            "api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
        user_token_headers: dict[str, str],
    ) -> None:
        response = client.delete(
            "api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=user_token_headers,
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}
