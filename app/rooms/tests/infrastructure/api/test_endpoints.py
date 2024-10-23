from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.rooms.application.create_room import CreateRoomParams


class TestCreateRoomEndpoint:
    @pytest.fixture
    def mock_application(self) -> Generator[Mock, None, None]:
        with patch("app.rooms.infrastructure.api.endpoints.CreateRoom") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.rooms.infrastructure.api.endpoints.SqlModelRoomRepository") as mock:
            yield mock.return_value

    def test_returns_201_and_calls_action(
        self,
        client: TestClient,
        mock_application: Mock,
        mock_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        response = client.post(
            "api/v1/rooms/",
            json={
                "name": "Room 1",
                "seat_configuration": [{"row": 1, "number": 1}],
            },
            headers=superuser_token_headers,
        )

        mock_application.assert_called_once_with(repository=mock_repository)
        mock_application.return_value.execute.assert_called_once_with(
            params=CreateRoomParams(
                name="Room 1",
                seat_configuration=[{"row": 1, "number": 1}],
            )
        )

        assert response.status_code == 201

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_application: Mock,
        mock_repository: Mock,
    ) -> None:
        response = client.post(
            "api/v1/rooms/",
            json={
                "name": "Room 1",
                "seat_configuration": [{"row": 1, "number": 1}],
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
            "api/v1/rooms/",
            json={
                "name": "Room 1",
                "seat_configuration": [{"row": 1, "number": 1}],
            },
            headers=user_token_headers,
        )

        mock_application.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}
