from dataclasses import dataclass

from app.rooms.domain.repositories.room_repository import RoomRepository
from app.rooms.domain.room import Room


@dataclass(frozen=True)
class CreateRoomParams:
    name: str
    seat_configuration: list[dict[str, int]]


class CreateRoom:
    def __init__(self, repository: RoomRepository):
        self.repository = repository

    def execute(self, params: CreateRoomParams) -> None:
        room = Room.create(params.name, params.seat_configuration)
        self.repository.create(room)
