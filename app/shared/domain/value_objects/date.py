from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Date:
    _value: date

    @property
    def value(self) -> date:
        return self._value

    @classmethod
    def from_datetime_date(cls, value: date) -> "Date":
        return cls(value)

    @classmethod
    def from_string(cls, value: str) -> "Date":
        return cls(date.fromisoformat(value))
