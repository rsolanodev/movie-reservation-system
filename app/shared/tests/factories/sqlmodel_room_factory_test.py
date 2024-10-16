import uuid
from uuid import UUID

from sqlmodel import Session

from app.rooms.infrastructure.models import RoomModel


class SqlModelRoomFactoryTest:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, name: str, seat_configuration: list[dict[str, int]], id: UUID | None = None) -> RoomModel:
        room_model = RoomModel(id=id or uuid.uuid4(), name=name, seat_configuration=seat_configuration)
        self._session.add(room_model)
        return room_model
