from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session

from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.seat_status import SeatStatus
from app.shared.tests.infrastructure.builders.sqlmodel_movie_builder import SqlModelMovieBuilder
from app.showtimes.domain.seat import Seat
from app.showtimes.infrastructure.finders.sqlmodel_seat_finder import SqlModelSeatFinder
from app.showtimes.tests.infrastructure.mothers.sqlmodel_seat_mother import SqlModelSeatMother


class TestSqlModelSeatFinder:
    def test_find_seats_by_showtime_id_ordered_by_row_and_number(self, session: Session) -> None:
        showtime_id = UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601")
        (
            SqlModelMovieBuilder(session)
            .with_id(UUID("ec725625-f502-4d39-9401-a415d8c1f964"))
            .with_showtime(
                id=showtime_id,
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
            )
            .build()
        )
        (
            SqlModelSeatMother(session)
            .with_id(UUID("b4087cea-0c32-40b3-87a4-e2a6aedc460f"))
            .with_showtime_id(showtime_id)
            .with_row(2)
            .with_number(1)
            .occupied()
            .create()
        )
        (
            SqlModelSeatMother(session)
            .with_id(UUID("537cc255-2e01-4f32-9ee2-eb56aded66ef"))
            .with_showtime_id(showtime_id)
            .with_row(1)
            .with_number(1)
            .available()
            .create()
        )
        (
            SqlModelSeatMother(session)
            .with_id(UUID("b43ecf0f-24f7-429e-bbce-5b389de2f297"))
            .with_showtime_id(showtime_id)
            .with_row(1)
            .with_number(2)
            .reserved()
            .create()
        )

        seats = SqlModelSeatFinder(session).find_seats_by_showtime_id(showtime_id=Id.from_uuid(showtime_id))

        assert seats == [
            Seat(id=Id("537cc255-2e01-4f32-9ee2-eb56aded66ef"), row=1, number=1, status=SeatStatus.AVAILABLE),
            Seat(id=Id("b43ecf0f-24f7-429e-bbce-5b389de2f297"), row=1, number=2, status=SeatStatus.RESERVED),
            Seat(id=Id("b4087cea-0c32-40b3-87a4-e2a6aedc460f"), row=2, number=1, status=SeatStatus.OCCUPIED),
        ]
