from datetime import datetime, timezone
from uuid import UUID

from freezegun import freeze_time
from sqlmodel import Session

from app.reservations.domain.collections.reservations import Reservations
from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.movie_show_reservation import Movie, MovieShowReservation, SeatLocation
from app.reservations.domain.reservation import CancellableReservation, Reservation
from app.reservations.infrastructure.finders.sqlmodel_reservation_finder import SqlModelReservationFinder
from app.reservations.tests.infrastructure.builders.sqlmodel_seat_builder import SqlModelSeatBuilder
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus
from app.shared.tests.infrastructure.builders.sqlmodel_movie_builder import SqlModelMovieBuilder
from app.shared.tests.infrastructure.builders.sqlmodel_reservation_builder import SqlModelReservationBuilder


@freeze_time("2025-01-10T12:00:00Z")
class TestSqlModelReservationFinder:
    def test_find_reservation(self, session: Session) -> None:
        reservation_model = (
            SqlModelReservationBuilder(session)
            .with_id(UUID("92ab35a6-ae79-4039-85b3-e8b2b8abb27d"))
            .with_user_id(UUID("47d653d5-971e-42c3-86ab-2c7f40ef783a"))
            .with_showtime_id(UUID("ffa502e6-8869-490c-8799-5bea26c7146d"))
            .build()
        )

        reservation = SqlModelReservationFinder(session).find_reservation(
            reservation_id=Id.from_uuid(reservation_model.id),
        )

        assert reservation == Reservation(
            id=Id("92ab35a6-ae79-4039-85b3-e8b2b8abb27d"),
            user_id=Id("47d653d5-971e-42c3-86ab-2c7f40ef783a"),
            showtime_id=Id("ffa502e6-8869-490c-8799-5bea26c7146d"),
            status=ReservationStatus.PENDING,
            created_at=DateTime.from_datetime(datetime(2025, 1, 10, 12, 0, 0)),
            provider_payment_id="pi_3MtwBwLkdIwHu7ix28a3tqPa",
            seats=Seats(),
        )

    def test_find_pending(self, session: Session) -> None:
        (
            SqlModelReservationBuilder(session)
            .with_id(UUID("92ab35a6-ae79-4039-85b3-e8b2b8abb27d"))
            .with_user_id(UUID("47d653d5-971e-42c3-86ab-2c7f40ef783a"))
            .with_showtime_id(UUID("ffa502e6-8869-490c-8799-5bea26c7146d"))
            .pending()
            .build()
        )
        SqlModelReservationBuilder(session).cancelled().build()
        SqlModelReservationBuilder(session).confirmed().build()
        SqlModelReservationBuilder(session).refunded().build()

        reservations = SqlModelReservationFinder(session).find_pending()

        assert reservations == Reservations(
            [
                Reservation(
                    id=Id("92ab35a6-ae79-4039-85b3-e8b2b8abb27d"),
                    user_id=Id("47d653d5-971e-42c3-86ab-2c7f40ef783a"),
                    showtime_id=Id("ffa502e6-8869-490c-8799-5bea26c7146d"),
                    status=ReservationStatus.PENDING,
                    created_at=DateTime.from_datetime(datetime(2025, 1, 10, 12, 0, 0)),
                    provider_payment_id="pi_3MtwBwLkdIwHu7ix28a3tqPa",
                    seats=Seats(),
                )
            ]
        )

    def test_find_movie_show_reservations_by_user_id(self, session: Session) -> None:
        (
            SqlModelMovieBuilder(session)
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
            SqlModelReservationBuilder(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .confirmed()
            .build()
        )
        (
            SqlModelSeatBuilder(session)
            .with_row(1)
            .with_number(2)
            .occupied()
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build()
        )

        reservations = SqlModelReservationFinder(session).find_movie_show_reservations_by_user_id(
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

    def test_find_movie_show_reservations_by_user_id_sorting_reservations_by_show_datetime_most_recent(
        self, session: Session
    ) -> None:
        (
            SqlModelMovieBuilder(session)
            .with_id(UUID("421d2efb-7523-43e1-ba97-f9057f08d468"))
            .with_title("La Sustancia")
            .with_poster_image("la_sustancia.jpg")
            .with_showtime(
                id=UUID("ef18bb4c-2109-443f-883d-cb48cfbddd58"),
                show_datetime=datetime(2023, 4, 3, 20, 0, tzinfo=timezone.utc),
            )
            .build(),
            SqlModelMovieBuilder(session)
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
            SqlModelReservationBuilder(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .confirmed()
            .build(),
            SqlModelReservationBuilder(session)
            .with_id(UUID("89ad8d2e-e9c1-4fd0-b2be-0e6295b6b886"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("ef18bb4c-2109-443f-883d-cb48cfbddd58"))
            .confirmed()
            .build(),
        )
        (
            SqlModelSeatBuilder(session)
            .with_row(1)
            .with_number(2)
            .occupied()
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build(),
            SqlModelSeatBuilder(session)
            .with_row(1)
            .with_number(3)
            .occupied()
            .with_reservation_id(UUID("89ad8d2e-e9c1-4fd0-b2be-0e6295b6b886"))
            .build(),
        )

        reservations = SqlModelReservationFinder(session).find_movie_show_reservations_by_user_id(
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

    def test_find_movie_show_reservations_by_user_id_sorting_seats_by_row_and_number(self, session: Session) -> None:
        (
            SqlModelMovieBuilder(session)
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
            SqlModelReservationBuilder(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .confirmed()
            .build(),
        )
        (
            SqlModelSeatBuilder(session)
            .with_row(1)
            .with_number(3)
            .occupied()
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build(),
            SqlModelSeatBuilder(session)
            .with_row(1)
            .with_number(2)
            .occupied()
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build(),
        )

        reservations = SqlModelReservationFinder(session).find_movie_show_reservations_by_user_id(
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

    def test_does_not_find_movie_show_reservations_by_user_id_when_user_id_does_not_exist(
        self, session: Session
    ) -> None:
        (
            SqlModelMovieBuilder(session)
            .with_showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
            .build()
        )
        (
            SqlModelReservationBuilder(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .confirmed()
            .build()
        )
        (
            SqlModelSeatBuilder(session)
            .occupied()
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .build()
        )

        reservations = SqlModelReservationFinder(session).find_movie_show_reservations_by_user_id(
            user_id=Id("cee0a37c-67bc-4038-a8fc-39e68ea1453a")
        )

        assert reservations == []

    def test_does_not_find_movie_show_reservations_by_user_id_when_reservation_is_pending(
        self, session: Session
    ) -> None:
        (
            SqlModelMovieBuilder(session)
            .with_showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            )
            .build()
        )
        (
            SqlModelReservationBuilder(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .pending()
            .build()
        )
        (
            SqlModelSeatBuilder(session)
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .reserved()
            .build()
        )

        reservations = SqlModelReservationFinder(session).find_movie_show_reservations_by_user_id(
            user_id=Id("bee0a37c-67bc-4038-a8fc-39e68ea1453a")
        )

        assert reservations == []

    def test_find_cancellable_reservation(self, session: Session) -> None:
        (
            SqlModelMovieBuilder(session)
            .with_showtime(
                id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                show_datetime=datetime(2025, 1, 11, 19, 0, 0, tzinfo=timezone.utc),
            )
            .build()
        )
        (
            SqlModelReservationBuilder(session)
            .with_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .with_user_id(UUID("bee0a37c-67bc-4038-a8fc-39e68ea1453a"))
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .confirmed()
            .build()
        )

        cancellable_reservation = SqlModelReservationFinder(session).find_cancellable_reservation(
            reservation_id=Id("a41707bd-ae9c-43b8-bba5-8c4844e73e77")
        )

        assert cancellable_reservation == CancellableReservation(
            reservation=Reservation(
                id=Id("a41707bd-ae9c-43b8-bba5-8c4844e73e77"),
                user_id=Id("bee0a37c-67bc-4038-a8fc-39e68ea1453a"),
                showtime_id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e601"),
                status=ReservationStatus.CONFIRMED,
                created_at=DateTime.from_datetime(datetime(2025, 1, 10, 12, 0, 0)),
                provider_payment_id="pi_3MtwBwLkdIwHu7ix28a3tqPa",
                seats=Seats(),
            ),
            show_datetime=DateTime.from_datetime(datetime(2025, 1, 11, 19, 0, 0)),
        )

    def test_does_not_find_cancellable_reservation_when_reservation_does_not_exist(self, session: Session) -> None:
        cancellable_reservation = SqlModelReservationFinder(session).find_cancellable_reservation(
            reservation_id=Id("a41707bd-ae9c-43b8-bba5-8c4844e73e77")
        )

        assert cancellable_reservation is None
