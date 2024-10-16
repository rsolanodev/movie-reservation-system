from app.rooms.domain.repositories.room_repository import RoomRepository
from app.rooms.domain.room import Room
from app.rooms.infrastructure.models import RoomModel
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository


class SqlModelRoomRepository(RoomRepository, SqlModelRepository):
    def create(self, room: Room) -> None:
        room_model = RoomModel.from_domain(room)
        self._session.add(room_model)
        self._session.commit()
