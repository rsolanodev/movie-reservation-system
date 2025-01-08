from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.rooms.application.commands.create_room import CreateRoomParams
from app.rooms.infrastructure.models import RoomModel


class TestCreateRoomEndpoint:
    @pytest.fixture
    def mock_create_room(self) -> Generator[Mock, None, None]:
        with patch("app.rooms.infrastructure.api.endpoints.CreateRoom") as mock:
            yield mock

    @pytest.fixture
    def mock_room_repository(self) -> Generator[Mock, None, None]:
        with patch("app.rooms.infrastructure.api.endpoints.SqlModelRoomRepository") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, session: Session, client: TestClient, superuser_token_headers: dict[str, str]) -> None:
        response = client.post(
            "api/v1/rooms/",
            json={
                "name": "Room 1",
                "seat_configuration": [{"row": 1, "number": 1}],
            },
            headers=superuser_token_headers,
        )

        assert response.status_code == 201

        room_model = session.exec(select(RoomModel)).first()
        assert room_model is not None
        assert room_model.name == "Room 1"
        assert room_model.seat_configuration == [{"row": 1, "number": 1}]

    def test_returns_201_and_calls_create_room(
        self,
        client: TestClient,
        mock_create_room: Mock,
        mock_room_repository: Mock,
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

        mock_create_room.assert_called_once_with(repository=mock_room_repository)
        mock_create_room.return_value.execute.assert_called_once_with(
            params=CreateRoomParams(
                name="Room 1",
                seat_configuration=[{"row": 1, "number": 1}],
            )
        )

        assert response.status_code == 201

    def test_returns_401_when_user_is_not_authenticated(
        self, client: TestClient, mock_create_room: Mock, mock_room_repository: Mock
    ) -> None:
        response = client.post(
            "api/v1/rooms/",
            json={
                "name": "Room 1",
                "seat_configuration": [{"row": 1, "number": 1}],
            },
        )

        mock_create_room.assert_not_called()
        mock_room_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_create_room: Mock,
        mock_room_repository: Mock,
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

        mock_create_room.assert_not_called()
        mock_room_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}
