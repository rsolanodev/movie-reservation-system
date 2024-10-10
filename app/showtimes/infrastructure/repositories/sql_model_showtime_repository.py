import uuid

from sqlmodel import select

from app.core.infrastructure.repositories.sql_model_repository import SqlModelRepository
from app.reservations.infrastructure.models import SeatModel, SeatStatus
from app.showtimes.domain.repositories.showtime_repository import ShowtimeRepository
from app.showtimes.domain.showtime import Showtime
from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelShowtimeRepository(ShowtimeRepository, SqlModelRepository):
    def exists(self, showtime: Showtime) -> bool:
        statement = select(ShowtimeModel).where(
            ShowtimeModel.movie_id == showtime.movie_id,
            ShowtimeModel.show_datetime == showtime.show_datetime,
            ShowtimeModel.room_id == showtime.room_id,
        )
        result = self._session.exec(statement).one_or_none()
        return result is not None

    def create(self, showtime: Showtime) -> None:
        showtime_model = ShowtimeModel.from_domain(showtime)
        self._session.add(showtime_model)
        self._session.commit()
        self._session.refresh(showtime_model)
        self._create_seats(showtime_model)

    def _create_seats(self, showtime_model: ShowtimeModel) -> None:
        seat_models: list[SeatModel] = []
        for seat_config in showtime_model.room.seat_configuration:
            seat_models.append(
                SeatModel(
                    showtime_id=showtime_model.id,
                    row=seat_config["row"],
                    number=seat_config["number"],
                    status=SeatStatus.AVAILABLE,
                ),
            )
        self._session.add_all(seat_models)
        self._session.commit()

    def delete(self, showtime_id: uuid.UUID) -> None:
        statement = select(ShowtimeModel).where(ShowtimeModel.id == showtime_id)
        showtime_model = self._session.exec(statement).first()
        if showtime_model:
            self._session.delete(showtime_model)
            self._session.commit()
