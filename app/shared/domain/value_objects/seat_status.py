from enum import StrEnum


class SeatStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"
