from enum import StrEnum


class ReservationStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    def is_confirmed(self) -> bool:
        return self == ReservationStatus.CONFIRMED
