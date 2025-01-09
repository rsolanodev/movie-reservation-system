from datetime import datetime, timezone
from unittest.mock import ANY
from uuid import UUID

from sqlmodel import Session

from app.shared.domain.value_objects.id import Id
from app.shared.tests.builders.sqlmodel_movie_builder_test import SqlModelMovieBuilderTest
from app.showtimes.domain.seat import Seat, SeatStatus
from app.showtimes.infrastructure.finders.sqlmodel_seat_finder import SqlModelSeatFinder
from app.showtimes.tests.factories.sqlmodel_seat_factory_test import SqlModelSeatFactoryTest


class TestSqlModelSeatFinder:
    def test_find_seats_by_showtime_id_ordered_by_row_and_number(self, session: Session) -> None:
        showtime_id = UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601")

        SqlModelMovieBuilderTest(session=session).with_id(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            id=showtime_id,
            show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
        ).build()

        seat_model_factory = SqlModelSeatFactoryTest(session=session)
        seat_model_factory.create(showtime_id=showtime_id, row=2, number=1, status=SeatStatus.OCCUPIED)
        seat_model_factory.create(showtime_id=showtime_id, row=1, number=1, status=SeatStatus.AVAILABLE)
        seat_model_factory.create(showtime_id=showtime_id, row=1, number=2, status=SeatStatus.RESERVED)
        seat_model_factory.create(row=1, number=1)

        seats = SqlModelSeatFinder(session=session).find_seats_by_showtime_id(
            showtime_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e601")
        )

        assert seats == [
            Seat(id=ANY, row=1, number=1, status=SeatStatus.AVAILABLE),
            Seat(id=ANY, row=1, number=2, status=SeatStatus.RESERVED),
            Seat(id=ANY, row=2, number=1, status=SeatStatus.OCCUPIED),
        ]
