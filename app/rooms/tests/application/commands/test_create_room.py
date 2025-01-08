from typing import Any
from unittest.mock import ANY, Mock, create_autospec

import pytest

from app.rooms.application.commands.create_room import CreateRoom, CreateRoomParams
from app.rooms.domain.repositories.room_repository import RoomRepository
from app.rooms.domain.room import Room


class TestCreateRoom:
    @pytest.fixture
    def mock_room_repository(self) -> Any:
        return create_autospec(spec=RoomRepository, instance=True, spec_set=True)

    def test_creates_room(self, mock_room_repository: Mock) -> None:
        CreateRoom(repository=mock_room_repository).execute(
            params=CreateRoomParams(name="Room 1", seat_configuration=[{"row": 1, "number": 1}])
        )

        mock_room_repository.create.assert_called_once_with(
            room=Room(id=ANY, name="Room 1", seat_configuration=[{"row": 1, "number": 1}])
        )
