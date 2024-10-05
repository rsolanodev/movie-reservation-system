from uuid import UUID

from sqlmodel import select

from app.core.infrastructure.repositories.sql_model_repository import SqlModelRepository
from app.movies.domain.repositories.movie_showtime_repository import (
    MovieShowtimeRepository,
)
from app.showtimes.domain.entities import Showtime
from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelMovieShowtimeRepository(MovieShowtimeRepository, SqlModelRepository):
    def get_by_movie_id(self, movie_id: UUID) -> list[Showtime]:
        statement = (
            select(ShowtimeModel)
            .where(ShowtimeModel.movie_id == movie_id)
            .order_by(ShowtimeModel.show_datetime)  # type: ignore
        )
        showtime_models = self._session.exec(statement).all()
        return [showtime_model.to_domain() for showtime_model in showtime_models]
