from enum import StrEnum


class ReservationStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    def is_pending(self) -> bool:
        return self == ReservationStatus.PENDING

    def is_confirmed(self) -> bool:
        return self == ReservationStatus.CONFIRMED

    def is_cancelled(self) -> bool:
        return self == ReservationStatus.CANCELLED

    def is_refunded(self) -> bool:
        return self == ReservationStatus.REFUNDED
