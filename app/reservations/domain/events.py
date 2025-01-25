from dataclasses import dataclass
from typing import Any, Self

from app.shared.domain.events.event import Event


@dataclass(frozen=True)
class ReservationCancelled(Event):
    reservation_id: str

    @classmethod
    def topic(cls) -> str:
        return "reservation.cancelled"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(reservation_id=data["reservation_id"])
