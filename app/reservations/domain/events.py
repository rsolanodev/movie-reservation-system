from dataclasses import dataclass
from typing import Any, Self

from app.shared.domain.events.event import Event


@dataclass(frozen=True)
class ReservationCancelled(Event):
    reservation_id: str
    provider_payment_id: str | None

    @classmethod
    def topic(cls) -> str:
        return "reservation.cancelled"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(reservation_id=data["reservation_id"], provider_payment_id=data["provider_payment_id"])
