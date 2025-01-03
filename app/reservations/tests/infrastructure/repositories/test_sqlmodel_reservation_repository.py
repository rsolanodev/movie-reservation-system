from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.movie_show_reservation import Movie, MovieShowReservation, SeatLocation
from app.reservations.domain.seat import SeatStatus
from app.reservations.infrastructure.models import ReservationModel
from app.reservations.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.reservations.tests.builders.reservation_builder_test import ReservationBuilderTest
from app.reservations.tests.builders.seat_builder_test import SeatBuilderTest
from app.reservations.tests.builders.sqlmodel_reservation_builder_test import SqlModelReservationBuilderTest
from app.reservations.tests.builders.sqlmodel_seat_builder_test import SqlModelSeatBuilderTest
from app.reservations.tests.factories.sqlmodel_seat_factory_test import SqlModelSeatFactoryTest
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.tests.builders.sqlmodel_movie_builder_test import SqlModelMovieBuilderTest


class TestSqlModelReservationRepository:
    def test_create_reservation_and_reserve_seats(self, session: Session) -> None:
        main_seat = SqlModelSeatFactoryTest(session).create_available()
        parent_seat = SqlModelSeatFactoryTest(session).create_available()

        reservation = (
            ReservationBuilderTest()
            .with_user_id(Id("47d653d5-971e-42c3-86ab-2c7f40ef783a"))
            .with_showtime_id(Id("ffa502e6-8869-490c-8799-5bea26c7146d"))
            .with_seats(
                Seats(
                    [
                        SeatBuilderTest().with_id(Id.from_uuid(main_seat.id)).build(),
                        SeatBuilderTest().with_id(Id.from_uuid(parent_seat.id)).build(),
                    ]
                ),
            )
            .build()
        )

        SqlModelReservationRepository(session).create(reservation)

        reservation_model = session.get_one(ReservationModel, reservation.id.to_uuid())
        assert reservation_model.user_id == UUID("47d653d5-971e-42c3-86ab-2c7f40ef783a")
        assert reservation_model.showtime_id == UUID("ffa502e6-8869-490c-8799-5bea26c7146d")

        session.refresh(main_seat)
        assert main_seat.reservation_id == reservation.id.to_uuid()
        assert main_seat.status == SeatStatus.RESERVED

        session.refresh(parent_seat)
        assert parent_seat.reservation_id == reservation.id.to_uuid()
        assert parent_seat.status == SeatStatus.RESERVED

    def test_release_reservation(self, session: Session) -> None:
        reservation_model = SqlModelReservationBuilderTest(session).build()
        seat_model = (
            SqlModelSeatBuilderTest(session)
            .with_status(SeatStatus.RESERVED)
            .with_reservation_id(reservation_model.id)
            .build()
        )

        SqlModelReservationRepository(session).release(
            reservation_id=Id.from_uuid(reservation_model.id),
        )

        assert seat_model.status == SeatStatus.AVAILABLE
        assert seat_model.reservation_id is None

    def test_find_by_user_id(self, session: Session) -> None:
        (
            SqlModelMovieBuilderTest(session=session)
            .with_id(UUID("8c8ec976-9692-4c86-921d-28cf1302550c"))
            .with_title("Robot Salvaje")
            .with_poster_image("robot_salvaje.jpg")
            .with_showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
            .build()
        )
        (
            SqlModelReservationBuilderTest(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .with_has_paid(True)
            .build()
        )
        (
            SqlModelSeatBuilderTest(session)
            .with_row(1)
            .with_number(2)
            .with_status(SeatStatus.OCCUPIED)
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build()
        )

        reservations = SqlModelReservationRepository(session).find_by_user_id(
            user_id=Id("bee0a37c-67bc-4038-a8fc-39e68ea1453a")
        )

        assert reservations == [
            MovieShowReservation(
                reservation_id=Id("a41707bd-ae9c-43b8-bba5-8c4844e73e77"),
                show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                movie=Movie(
                    id=Id("8c8ec976-9692-4c86-921d-28cf1302550c"),
                    title="Robot Salvaje",
                    poster_image="robot_salvaje.jpg",
                ),
                seats=[SeatLocation(row=1, number=2)],
            )
        ]

    def test_find_by_user_id_sorting_reservations_by_show_datetime_most_recent(self, session: Session) -> None:
        (
            SqlModelMovieBuilderTest(session=session)
            .with_id(UUID("421d2efb-7523-43e1-ba97-f9057f08d468"))
            .with_title("La Sustancia")
            .with_poster_image("la_sustancia.jpg")
            .with_showtime(
                id=UUID("ef18bb4c-2109-443f-883d-cb48cfbddd58"),
                show_datetime=datetime(2023, 4, 3, 20, 0, tzinfo=timezone.utc),
            )
            .build(),
            SqlModelMovieBuilderTest(session=session)
            .with_id(UUID("8c8ec976-9692-4c86-921d-28cf1302550c"))
            .with_title("Robot Salvaje")
            .with_poster_image("robot_salvaje.jpg")
            .with_showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
            .build(),
        )
        (
            SqlModelReservationBuilderTest(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .with_has_paid(True)
            .build(),
            SqlModelReservationBuilderTest(session)
            .with_id(UUID("89ad8d2e-e9c1-4fd0-b2be-0e6295b6b886"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("ef18bb4c-2109-443f-883d-cb48cfbddd58"))
            .with_has_paid(True)
            .build(),
        )
        (
            SqlModelSeatBuilderTest(session)
            .with_row(1)
            .with_number(2)
            .with_status(SeatStatus.OCCUPIED)
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build(),
            SqlModelSeatBuilderTest(session)
            .with_row(1)
            .with_number(3)
            .with_status(SeatStatus.OCCUPIED)
            .with_reservation_id(UUID("89ad8d2e-e9c1-4fd0-b2be-0e6295b6b886"))
            .build(),
        )

        reservations = SqlModelReservationRepository(session).find_by_user_id(
            user_id=Id("bee0a37c-67bc-4038-a8fc-39e68ea1453a")
        )

        assert reservations == [
            MovieShowReservation(
                reservation_id=Id("a41707bd-ae9c-43b8-bba5-8c4844e73e77"),
                show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                movie=Movie(
                    id=Id("8c8ec976-9692-4c86-921d-28cf1302550c"),
                    title="Robot Salvaje",
                    poster_image="robot_salvaje.jpg",
                ),
                seats=[SeatLocation(row=1, number=2)],
            ),
            MovieShowReservation(
                reservation_id=Id("89ad8d2e-e9c1-4fd0-b2be-0e6295b6b886"),
                show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 20, 0)),
                movie=Movie(
                    id=Id("421d2efb-7523-43e1-ba97-f9057f08d468"),
                    title="La Sustancia",
                    poster_image="la_sustancia.jpg",
                ),
                seats=[SeatLocation(row=1, number=3)],
            ),
        ]

    def test_find_by_user_id_sorting_seats_by_row_and_number(self, session: Session) -> None:
        (
            SqlModelMovieBuilderTest(session=session)
            .with_id(UUID("8c8ec976-9692-4c86-921d-28cf1302550c"))
            .with_title("Robot Salvaje")
            .with_poster_image("robot_salvaje.jpg")
            .with_showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
            .build(),
        )
        (
            SqlModelReservationBuilderTest(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .with_has_paid(True)
            .build(),
        )
        (
            SqlModelSeatBuilderTest(session)
            .with_row(1)
            .with_number(3)
            .with_status(SeatStatus.OCCUPIED)
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build(),
            SqlModelSeatBuilderTest(session)
            .with_row(1)
            .with_number(2)
            .with_status(SeatStatus.OCCUPIED)
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build(),
        )

        reservations = SqlModelReservationRepository(session).find_by_user_id(
            user_id=Id("bee0a37c-67bc-4038-a8fc-39e68ea1453a")
        )

        assert reservations == [
            MovieShowReservation(
                reservation_id=Id("a41707bd-ae9c-43b8-bba5-8c4844e73e77"),
                show_datetime=DateTime.from_datetime(datetime(2023, 4, 3, 22, 0)),
                movie=Movie(
                    id=Id("8c8ec976-9692-4c86-921d-28cf1302550c"),
                    title="Robot Salvaje",
                    poster_image="robot_salvaje.jpg",
                ),
                seats=[SeatLocation(row=1, number=2), SeatLocation(row=1, number=3)],
            ),
        ]

    def test_does_not_find_by_user_id_when_user_id_does_not_exist(self, session: Session) -> None:
        (
            SqlModelMovieBuilderTest(session=session)
            .with_showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
            .build()
        )
        (
            SqlModelReservationBuilderTest(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .with_has_paid(True)
            .build()
        )
        (
            SqlModelSeatBuilderTest(session)
            .with_status(SeatStatus.OCCUPIED)
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build()
        )

        reservations = SqlModelReservationRepository(session).find_by_user_id(
            user_id=Id("cee0a37c-67bc-4038-a8fc-39e68ea1453a")
        )

        assert reservations == []

    def test_does_not_find_by_user_id_when_does_not_have_seats_occupied(self, session: Session) -> None:
        (
            SqlModelMovieBuilderTest(session=session)
            .with_showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
            .build()
        )
        (
            SqlModelReservationBuilderTest(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .with_has_paid(True)
            .build()
        )
        (
            SqlModelSeatBuilderTest(session)
            .with_status(SeatStatus.RESERVED)
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build()
        )

        reservations = SqlModelReservationRepository(session).find_by_user_id(
            user_id=Id("bee0a37c-67bc-4038-a8fc-39e68ea1453a")
        )

        assert reservations == []
