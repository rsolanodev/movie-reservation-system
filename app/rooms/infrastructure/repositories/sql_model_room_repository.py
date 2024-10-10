from app.core.infrastructure.repositories.sql_model_repository import SqlModelRepository
from app.rooms.domain.repositories.room_repository import RoomRepository
from app.rooms.domain.room import Room
from app.rooms.infrastructure.models import RoomModel


class SqlModelRoomRepository(RoomRepository, SqlModelRepository):
    def create(self, room: Room) -> None:
        room_model = RoomModel.from_domain(room)
        self._session.add(room_model)
        self._session.commit()
