from sqlmodel import Session

from app.rooms.domain.room import Room
from app.rooms.infrastructure.models import RoomModel
from app.rooms.infrastructure.repositories.sql_model_room_repository import SqlModelRoomRepository


class TestSqlModelRoomRepository:
    def test_create_room(self, session: Session) -> None:
        room = Room.create(name="Room 1", seat_configuration=[{"row": 1, "number": 1}])
        SqlModelRoomRepository(session=session).create(room)

        room_model = session.get_one(RoomModel, room.id)
        assert room_model.name == "Room 1"
        assert room_model.seat_configuration == [{"row": 1, "number": 1}]
