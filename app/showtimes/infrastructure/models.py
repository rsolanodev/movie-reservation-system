import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from app.movies.infrastructure.models import MovieModel


class ShowtimeModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    movie_id: uuid.UUID = Field(foreign_key="moviemodel.id")
    show_datetime: datetime
    movie: MovieModel = Relationship(back_populates="showtimes")
