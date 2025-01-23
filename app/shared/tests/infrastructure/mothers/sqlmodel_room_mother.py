from typing import Self
from uuid import UUID

from sqlmodel import Session

from app.rooms.infrastructure.models import RoomModel


class SqlModelRoomMother:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._room = RoomModel(
            id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
            name="Room 1",
            seat_configuration=[{"row": 1, "number": 2}],
        )

    def with_seat_configuration(self, seat_configuration: list[dict[str, int]]) -> Self:
        self._room.seat_configuration = seat_configuration
        return self

    def create(self) -> RoomModel:
        self._session.add(self._room)
        return self._room
