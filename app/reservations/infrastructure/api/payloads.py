from uuid import UUID

from sqlmodel import SQLModel


class CreateReservationPayload(SQLModel):
    showtime_id: UUID
    seat_ids: list[UUID]
