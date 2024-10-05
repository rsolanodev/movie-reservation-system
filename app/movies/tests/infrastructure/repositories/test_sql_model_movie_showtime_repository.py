from datetime import datetime
from uuid import UUID

from sqlmodel import Session

from app.movies.infrastructure.repositories.sql_model_movie_showtime_repository import (
    SqlModelMovieShowtimeRepository,
)
from app.shared.tests.infrastructure.builders.movie_model_builder import (
    MovieModelBuilder,
)
from app.shared.tests.infrastructure.factories.showtime_model_factory import (
    ShowtimeModelFactory,
)
from app.showtimes.domain.entities import Showtime


class TestSqlModelMovieShowtimeRepository:
    def test_get_showtimes_by_movie_id(self, session: Session) -> None:
        movie_model = (
            MovieModelBuilder(session=session)
            .with_id(id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_showtime(
                showtime_model=ShowtimeModelFactory(session=session).create(
                    id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                    movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                    show_datetime=datetime(2023, 4, 3, 20, 0),
                )
            )
            .with_showtime(
                showtime_model=ShowtimeModelFactory(session=session).create(
                    id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                    movie_id=UUID("ec725625-f502-4d39-9401-a415d8c1f964"),
                    show_datetime=datetime(2023, 4, 3, 22, 0),
                )
            )
            .build()
        )
        repository = SqlModelMovieShowtimeRepository(session=session)
        showtimes = repository.get_by_movie_id(movie_model.id)

        assert showtimes == [
            Showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
                movie_id=movie_model.id,
                show_datetime=datetime(2023, 4, 3, 20, 0),
            ),
            Showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                movie_id=movie_model.id,
                show_datetime=datetime(2023, 4, 3, 22, 0),
            ),
        ]

    def test_get_by_movie_id_no_showtimes(self, session: Session) -> None:
        movie_model = MovieModelBuilder(session=session).build()

        repository = SqlModelMovieShowtimeRepository(session=session)
        showtimes = repository.get_by_movie_id(movie_model.id)

        assert showtimes == []
