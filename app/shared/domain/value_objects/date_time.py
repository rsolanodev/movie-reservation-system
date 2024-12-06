from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class DateTime:
    _value: datetime

    @classmethod
    def from_datetime(cls, value: datetime) -> "DateTime":
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return cls(value)

    @classmethod
    def now(cls) -> "DateTime":
        return cls.from_datetime(datetime.now(timezone.utc))

    def to_string(self) -> str:
        return self._value.strftime("%Y-%m-%dT%H:%M:%SZ")

    def __ge__(self, other: "DateTime") -> bool:
        return self._value >= other._value
