from sqlmodel import SQLModel


class CreateReservationPayload(SQLModel):
    showtime_id: str
    seat_ids: list[str]
