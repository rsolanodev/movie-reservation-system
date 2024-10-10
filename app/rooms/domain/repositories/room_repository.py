from typing import Protocol

from app.rooms.domain.room import Room


class RoomRepository(Protocol):
    def create(self, room: Room) -> None: ...
