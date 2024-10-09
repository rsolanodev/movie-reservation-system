import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.showtimes.domain.entities import Showtime

if TYPE_CHECKING:
    from app.movies.infrastructure.models import MovieModel


class ShowtimeModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    show_datetime: datetime
    movie_id: uuid.UUID = Field(foreign_key="moviemodel.id")
    movie: "MovieModel" = Relationship(back_populates="showtimes")

    @classmethod
    def from_domain(cls, showtime: Showtime) -> "ShowtimeModel":
        return ShowtimeModel(
            id=showtime.id,
            movie_id=showtime.movie_id,
            show_datetime=showtime.show_datetime,
        )

    def to_domain(self) -> Showtime:
        return Showtime(
            id=self.id,
            movie_id=self.movie_id,
            show_datetime=self.show_datetime,
        )
