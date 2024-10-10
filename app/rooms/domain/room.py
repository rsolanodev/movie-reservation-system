import uuid
from dataclasses import dataclass


@dataclass
class Room:
    id: uuid.UUID
    name: str
    seat_configuration: list[dict[str, int]]

    @classmethod
    def create(cls, name: str, seat_configuration: list[dict[str, int]]) -> "Room":
        return cls(id=uuid.uuid4(), name=name, seat_configuration=seat_configuration)
