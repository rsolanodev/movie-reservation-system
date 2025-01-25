from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Id:
    _value: str

    @property
    def value(self) -> str:
        return self._value

    @classmethod
    def from_uuid(cls, uuid: UUID) -> "Id":
        return cls(str(uuid))

    def to_uuid(self) -> UUID:
        return UUID(self._value)
