from datetime import datetime
from uuid import UUID

from sqlmodel import Session

from app.shared.tests.infrastructure.builders.movie_model_builder import (
    MovieModelBuilder,
)
from app.shared.tests.infrastructure.factories.showtime_model_factory import (
    ShowtimeModelFactory,
)
from app.showtimes.domain.entities import Showtime
from app.showtimes.infrastructure.models import ShowtimeModel
from app.showtimes.infrastructure.repositories.sql_model_showtime_repository import (
    SqlModelShowtimeRepository,
)


class TestSqlModelShowtimeRepository:
    def test_exists_showtime(self, session: Session) -> None:
        movie_model = (
            MovieModelBuilder(session=session)
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_showtime(
                showtime_model=ShowtimeModelFactory(session=session).create(
                    movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                    show_datetime=datetime(2023, 4, 1, 20, 0),
                )
            )
            .build()
        )
        repository = SqlModelShowtimeRepository(session=session)
        assert repository.exists(movie_model.id, datetime(2023, 4, 1, 20, 0)) is True

    def test_does_not_exist_showtime(self, session: Session) -> None:
        movie_model = MovieModelBuilder(session=session).build()

        repository = SqlModelShowtimeRepository(session=session)
        assert repository.exists(movie_model.id, datetime(2023, 4, 2, 20, 0)) is False

    def test_create_showtime(self, session: Session) -> None:
        showtime = Showtime.create(
            movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            show_datetime=datetime(2023, 4, 2, 20, 0),
        )
        SqlModelShowtimeRepository(session=session).create(showtime)

        showtime_model = session.get(ShowtimeModel, showtime.id)
        assert showtime_model is not None
        assert showtime_model.movie_id == UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        assert showtime_model.show_datetime == datetime(2023, 4, 2, 20, 0)

    def test_delete_showtime(self, session: Session) -> None:
        ShowtimeModelFactory(session=session).create(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
            movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
            show_datetime=datetime(2023, 4, 1, 20, 0),
        )

        SqlModelShowtimeRepository(session=session).delete(
            showtime_id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600")
        )

        showtime_model = session.get(
            ShowtimeModel, UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600")
        )
        assert showtime_model is None
