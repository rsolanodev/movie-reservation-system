from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class DateTime:
    _value: datetime

    @property
    def value(self) -> datetime:
        return self._value

    def subtract_minutes(self, minutes: int) -> "DateTime":
        return self.from_datetime(self._value - timedelta(minutes=minutes))

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

    @classmethod
    def from_string(cls, value: str) -> "DateTime":
        return cls.from_datetime(datetime.fromisoformat(value))

    def __ge__(self, other: "DateTime") -> bool:
        return self._value >= other._value

    def __lt__(self, other: "DateTime") -> bool:
        return self._value < other._value
