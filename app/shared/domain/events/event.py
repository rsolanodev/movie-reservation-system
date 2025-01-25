from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Self


@dataclass(frozen=True)
class Event(ABC):
    @classmethod
    @abstractmethod
    def topic(cls) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
