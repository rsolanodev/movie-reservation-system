import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.shared.domain.value_objects.id import Id
from app.showtimes.domain.showtime import Showtime

if TYPE_CHECKING:
    from app.movies.infrastructure.models import MovieModel
    from app.reservations.infrastructure.models import ReservationModel, SeatModel
    from app.rooms.infrastructure.models import RoomModel


class ShowtimeModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    show_datetime: datetime
    movie_id: uuid.UUID = Field(foreign_key="moviemodel.id")
    room_id: uuid.UUID = Field(foreign_key="roommodel.id")
    movie: "MovieModel" = Relationship(back_populates="showtimes")
    room: "RoomModel" = Relationship(back_populates="showtimes")
    seats: list["SeatModel"] = Relationship(back_populates="showtime")
    reservations: list["ReservationModel"] = Relationship(back_populates="showtime")

    @classmethod
    def from_domain(cls, showtime: Showtime) -> "ShowtimeModel":
        return ShowtimeModel(
            id=showtime.id.to_uuid(),
            movie_id=showtime.movie_id.to_uuid(),
            room_id=showtime.room_id.to_uuid(),
            show_datetime=showtime.show_datetime,
        )

    def to_domain(self) -> Showtime:
        return Showtime(
            id=Id.from_uuid(self.id),
            movie_id=Id.from_uuid(self.movie_id),
            room_id=Id.from_uuid(self.room_id),
            show_datetime=self.show_datetime,
        )
