from sqlmodel import SQLModel


class CreateRoomPayload(SQLModel):
    name: str
    seat_configuration: list[dict[str, int]]
