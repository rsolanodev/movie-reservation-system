import uuid
from dataclasses import dataclass

from app.shared.domain.value_objects.id import Id


@dataclass
class Room:
    id: Id
    name: str
    seat_configuration: list[dict[str, int]]

    @classmethod
    def create(cls, name: str, seat_configuration: list[dict[str, int]]) -> "Room":
        return cls(id=Id.from_uuid(uuid.uuid4()), name=name, seat_configuration=seat_configuration)
