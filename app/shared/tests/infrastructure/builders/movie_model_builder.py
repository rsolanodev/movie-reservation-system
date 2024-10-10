import uuid
from datetime import datetime

from sqlmodel import Session

from app.movies.infrastructure.models import GenreModel, MovieModel
from app.shared.tests.infrastructure.builders.showtime_model_builder import ShowtimeModelBuilder
from app.showtimes.infrastructure.models import ShowtimeModel


class MovieModelBuilder:
    def __init__(self, session: Session) -> None:
        self._session = session

        self.id: uuid.UUID = uuid.uuid4()
        self.title: str = "Deadpool & Wolverine"
        self.description: str = "Deadpool and a variant of Wolverine."
        self.poster_image: str | None = "deadpool_and_wolverine.jpg"

        self.genres: list[GenreModel] = []
        self.showtimes: list[ShowtimeModel] = []

    def with_id(self, id: uuid.UUID) -> "MovieModelBuilder":
        self.id = id
        return self

    def with_title(self, title: str) -> "MovieModelBuilder":
        self.title = title
        return self

    def with_description(self, description: str) -> "MovieModelBuilder":
        self.description = description
        return self

    def with_poster_image(self, poster_image: str | None) -> "MovieModelBuilder":
        self.poster_image = poster_image
        return self

    def with_genre(self, genre_model: GenreModel) -> "MovieModelBuilder":
        self.genres.append(genre_model)
        return self

    def with_showtime(
        self, show_datetime: datetime, id: uuid.UUID | None = None, room_id: uuid.UUID | None = None
    ) -> "MovieModelBuilder":
        showtime_model = (
            ShowtimeModelBuilder(session=self._session)
            .with_id(id=id or uuid.uuid4())
            .with_movie_id(movie_id=self.id)
            .with_room_id(room_id=room_id or uuid.uuid4())
            .with_show_datetime(show_datetime=show_datetime)
            .build()
        )
        self.showtimes.append(showtime_model)
        return self

    def build(self) -> MovieModel:
        movie_model = MovieModel(
            id=self.id,
            title=self.title,
            description=self.description,
            poster_image=self.poster_image,
            genres=self.genres,
            showtimes=self.showtimes,
        )
        self._session.add(movie_model)
        return movie_model
