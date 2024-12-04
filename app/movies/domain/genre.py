import uuid
from dataclasses import dataclass

from app.shared.domain.value_objects.id import ID


@dataclass
class Genre:
    id: ID
    name: str

    @classmethod
    def create(cls, name: str) -> "Genre":
        return cls(id=ID.from_uuid(uuid.uuid4()), name=name)
