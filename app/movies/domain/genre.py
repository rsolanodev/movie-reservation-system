import uuid
from dataclasses import dataclass

from app.shared.domain.value_objects.id import Id


@dataclass
class Genre:
    id: Id
    name: str

    @classmethod
    def create(cls, name: str) -> "Genre":
        return cls(id=Id.from_uuid(uuid.uuid4()), name=name)
