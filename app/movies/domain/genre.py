import uuid
from dataclasses import dataclass


@dataclass
class Genre:
    id: uuid.UUID
    name: str

    @classmethod
    def create(cls, name: str) -> "Genre":
        return cls(id=uuid.uuid4(), name=name)
