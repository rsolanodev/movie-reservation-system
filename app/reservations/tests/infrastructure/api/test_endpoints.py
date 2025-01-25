from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from freezegun import freeze_time
from sqlmodel import Session

from app.reservations.application.commands.cancel_reservation import CancelReservationParams
from app.reservations.application.commands.create_reservation import CreateReservationParams
from app.reservations.domain.exceptions import (
    CancellationNotAllowed,
    ReservationNotFound,
    SeatsNotAvailable,
    UnauthorizedCancellation,
)
from app.reservations.domain.movie_show_reservation import Movie, MovieShowReservation, SeatLocation
from app.reservations.tests.infrastructure.builders.sqlmodel_seat_builder import SqlModelSeatBuilder
from app.shared.domain.payment_intent import PaymentIntent
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus
from app.shared.domain.value_objects.seat_status import SeatStatus
from app.shared.tests.infrastructure.builders.sqlmodel_movie_builder import SqlModelMovieBuilder
from app.shared.tests.infrastructure.builders.sqlmodel_reservation_builder import SqlModelReservationBuilder
from app.shared.tests.infrastructure.builders.sqlmodel_showtime_builder import SqlModelShowtimeBuilder
from app.users.infrastructure.models import UserModel


class TestCreateReservationEndpoint:
    @pytest.fixture
    def mock_create_reservation(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.CreateReservation") as mock:
            yield mock

    @pytest.fixture
    def mock_reservation_repository(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.SqlModelReservationRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_seat_finder(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.SqlModelSeatFinder") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_stripe_client(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.StripeClient") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(
        self,
        session: Session,
        client: TestClient,
        user_token_headers: dict[str, str],
        user: UserModel,
        mock_stripe_client: Mock,
    ) -> None:
        seat = SqlModelSeatBuilder(session).available().build()

        mock_stripe_client.create_payment_intent.return_value = PaymentIntent(
            client_secret="test_client_secret",
            provider_payment_id="test_payment_id",
            amount=42.99,
        )
        response = client.post(
            "api/v1/reservations/",
            json={"showtime_id": str(seat.showtime_id), "seat_ids": [str(seat.id)]},
            headers=user_token_headers,
        )

        assert response.status_code == 201
        assert response.json() == {
            "client_secret": "test_client_secret",
            "provider_payment_id": "test_payment_id",
            "amount": 42.99,
        }

        session.refresh(seat)
        assert seat.status == SeatStatus.RESERVED
        assert seat.reservation_id is not None
        assert seat.reservation.user_id == user.id
        assert seat.reservation.provider_payment_id == "test_payment_id"

    def test_returns_201_and_calls_create_reservation(
        self,
        client: TestClient,
        mock_create_reservation: Mock,
        mock_reservation_repository: Mock,
        mock_seat_finder: Mock,
        mock_stripe_client: Mock,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
        mock_create_reservation.return_value.execute.return_value = PaymentIntent(
            client_secret="test_client_secret",
            provider_payment_id="test_payment_id",
            amount=42.99,
        )

        response = client.post(
            "api/v1/reservations/",
            json={
                "showtime_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "seat_ids": ["b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1"],
            },
            headers=user_token_headers,
        )

        mock_create_reservation.assert_called_once_with(
            reservation_repository=mock_reservation_repository,
            seat_finder=mock_seat_finder,
            payment_client=mock_stripe_client,
        )
        mock_create_reservation.return_value.execute.assert_called_once_with(
            params=CreateReservationParams(
                showtime_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                seat_ids=[Id("b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1")],
                user_id=Id.from_uuid(user.id),
            )
        )

        assert response.status_code == 201
        assert response.json() == {
            "client_secret": "test_client_secret",
            "provider_payment_id": "test_payment_id",
            "amount": 42.99,
        }

    def test_returns_400_when_seats_not_available(
        self,
        client: TestClient,
        mock_create_reservation: Mock,
        mock_reservation_repository: Mock,
        mock_seat_finder: Mock,
        mock_stripe_client: Mock,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
        mock_create_reservation.return_value.execute.side_effect = SeatsNotAvailable

        response = client.post(
            "api/v1/reservations/",
            json={
                "showtime_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "seat_ids": ["b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1"],
            },
            headers=user_token_headers,
        )

        mock_create_reservation.assert_called_once_with(
            reservation_repository=mock_reservation_repository,
            seat_finder=mock_seat_finder,
            payment_client=mock_stripe_client,
        )
        mock_create_reservation.return_value.execute.assert_called_once_with(
            params=CreateReservationParams(
                showtime_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                seat_ids=[Id("b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1")],
                user_id=Id.from_uuid(user.id),
            )
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Seats not available"}

    def test_returns_401_when_user_is_not_authenticated(
        self, client: TestClient, mock_create_reservation: Mock
    ) -> None:
        response = client.post(
            "api/v1/reservations/",
            json={
                "showtime_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "seat_ids": ["b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1"],
            },
        )

        mock_create_reservation.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


class TestListReservationsEndpoint:
    @pytest.fixture
    def mock_find_reservations(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.FindReservations") as mock:
            yield mock

    @pytest.fixture
    def mock_reservation_finder(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.SqlModelReservationFinder") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(
        self,
        session: Session,
        client: TestClient,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
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
            .with_user_id(user.id)
            .with_showtime_id(UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601"))
            .confirmed()
            .build()
        )
        (
            SqlModelSeatBuilder(session)
            .with_row(1)
            .with_number(2)
            .with_reservation_id(UUID("a41707bd-ae9c-43b8-bba5-8c4844e73e77"))
            .occupied()
            .build()
        )

        response = client.get("api/v1/reservations/", headers=user_token_headers)

        assert response.status_code == 200
        assert response.json() == [
            {
                "reservation_id": "a41707bd-ae9c-43b8-bba5-8c4844e73e77",
                "show_datetime": "2023-04-03T22:00:00Z",
                "movie": {
                    "id": "8c8ec976-9692-4c86-921d-28cf1302550c",
                    "title": "Robot Salvaje",
                    "poster_image": "robot_salvaje.jpg",
                },
                "seats": [{"row": 1, "number": 2}],
            }
        ]

    def test_returns_200_and_calls_find_reservations(
        self,
        client: TestClient,
        mock_find_reservations: Mock,
        mock_reservation_finder: Mock,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
        mock_find_reservations.return_value.execute.return_value = [
            MovieShowReservation(
                reservation_id=Id("5661455d-de5a-47ba-b99f-f6d50fdfc00b"),
                show_datetime=DateTime.from_datetime(datetime(2024, 1, 2, 22, 0)),
                movie=Movie(
                    id=Id("d64a9a87-4484-46f9-8ec1-f1e1c9fe2880"),
                    title="Robot Salvaje",
                    poster_image="robot_salvaje.jpg",
                ),
                seats=[SeatLocation(row=1, number=2)],
            ),
            MovieShowReservation(
                reservation_id=Id("ffd7e9f4-bec7-4487-8f2f-d84b49d0bcee"),
                show_datetime=DateTime.from_datetime(datetime(2024, 1, 1, 20, 0)),
                movie=Movie(
                    id=Id("6c42605f-ac4a-405d-94f2-1f0ea3de5ddb"),
                    title="La Sustancia",
                    poster_image="la_sustancia.jpg",
                ),
                seats=[SeatLocation(row=3, number=4)],
            ),
        ]

        response = client.get("api/v1/reservations/", headers=user_token_headers)

        mock_find_reservations.assert_called_once_with(finder=mock_reservation_finder)
        mock_find_reservations.return_value.execute.assert_called_once_with(user_id=Id.from_uuid(user.id))

        assert response.status_code == 200
        assert response.json() == [
            {
                "reservation_id": "5661455d-de5a-47ba-b99f-f6d50fdfc00b",
                "show_datetime": "2024-01-02T22:00:00Z",
                "movie": {
                    "id": "d64a9a87-4484-46f9-8ec1-f1e1c9fe2880",
                    "title": "Robot Salvaje",
                    "poster_image": "robot_salvaje.jpg",
                },
                "seats": [{"row": 1, "number": 2}],
            },
            {
                "reservation_id": "ffd7e9f4-bec7-4487-8f2f-d84b49d0bcee",
                "show_datetime": "2024-01-01T20:00:00Z",
                "movie": {
                    "id": "6c42605f-ac4a-405d-94f2-1f0ea3de5ddb",
                    "title": "La Sustancia",
                    "poster_image": "la_sustancia.jpg",
                },
                "seats": [{"row": 3, "number": 4}],
            },
        ]

    def test_returns_401_when_user_is_not_authenticated(
        self, client: TestClient, mock_find_reservations: Mock, mock_reservation_finder: Mock
    ) -> None:
        response = client.get("api/v1/reservations/")

        mock_find_reservations.assert_not_called()
        mock_reservation_finder.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


class TestCancelReservationEndpoint:
    @pytest.fixture
    def mock_cancel_reservation(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.CancelReservation") as mock:
            yield mock

    @pytest.fixture
    def mock_reservation_repository(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.SqlModelReservationRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_reservation_finder(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.SqlModelReservationFinder") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_event_bus(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.RabbitMQEventBus") as mock:
            yield mock.return_value

    @pytest.mark.integration
    @freeze_time("2025-01-22T21:00:00Z")
    def test_integration(
        self,
        session: Session,
        client: TestClient,
        user_token_headers: dict[str, str],
        user: UserModel,
        mock_event_bus: Mock,
    ) -> None:
        showtime_model = (
            SqlModelShowtimeBuilder(session)
            .with_show_datetime(datetime(2025, 1, 22, 22, 0, tzinfo=timezone.utc))
            .build()
        )
        reservation_model = (
            SqlModelReservationBuilder(session)
            .with_id(UUID("5661455d-de5a-47ba-b99f-f6d50fdfc00b"))
            .with_user_id(user.id)
            .with_showtime_id(showtime_model.id)
            .confirmed()
            .build()
        )
        seat_model = (
            SqlModelSeatBuilder(session)
            .with_row(1)
            .with_number(2)
            .occupied()
            .with_reservation_id(reservation_model.id)
            .build()
        )

        response = client.delete(
            "api/v1/reservations/5661455d-de5a-47ba-b99f-f6d50fdfc00b/", headers=user_token_headers
        )

        mock_event_bus.publish.assert_called_once()

        assert response.status_code == 204
        assert reservation_model.status == ReservationStatus.CANCELLED.value
        assert seat_model.status == SeatStatus.AVAILABLE.value

    def test_returns_204_and_calls_cancel_reservation(
        self,
        client: TestClient,
        mock_cancel_reservation: Mock,
        mock_reservation_repository: Mock,
        mock_reservation_finder: Mock,
        mock_event_bus: Mock,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
        response = client.delete(
            "api/v1/reservations/5661455d-de5a-47ba-b99f-f6d50fdfc00b/", headers=user_token_headers
        )

        mock_cancel_reservation.assert_called_once_with(
            finder=mock_reservation_finder, repository=mock_reservation_repository, event_bus=mock_event_bus
        )
        mock_cancel_reservation.return_value.execute.assert_called_once_with(
            params=CancelReservationParams(
                reservation_id=Id("5661455d-de5a-47ba-b99f-f6d50fdfc00b"), user_id=Id.from_uuid(user.id)
            )
        )

        assert response.status_code == 204

    def test_returns_401_when_user_is_not_authenticated(
        self, client: TestClient, mock_cancel_reservation: Mock
    ) -> None:
        response = client.delete("api/v1/reservations/5661455d-de5a-47ba-b99f-f6d50fdfc00b/")

        mock_cancel_reservation.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_404_when_reservation_does_not_exist(
        self, client: TestClient, mock_cancel_reservation: Mock, user_token_headers: dict[str, str], user: UserModel
    ) -> None:
        mock_cancel_reservation.return_value.execute.side_effect = ReservationNotFound

        response = client.delete(
            "api/v1/reservations/5661455d-de5a-47ba-b99f-f6d50fdfc00b/", headers=user_token_headers
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Reservation not found"}

    def test_returns_400_when_reservation_does_not_belong_to_user(
        self, client: TestClient, mock_cancel_reservation: Mock, user_token_headers: dict[str, str]
    ) -> None:
        mock_cancel_reservation.return_value.execute.side_effect = UnauthorizedCancellation

        response = client.delete(
            "api/v1/reservations/5661455d-de5a-47ba-b99f-f6d50fdfc00b/", headers=user_token_headers
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Unauthorized to cancel this reservation"}

    def test_returns_400_when_showtime_has_started(
        self, client: TestClient, mock_cancel_reservation: Mock, user_token_headers: dict[str, str]
    ) -> None:
        mock_cancel_reservation.return_value.execute.side_effect = CancellationNotAllowed

        response = client.delete(
            "api/v1/reservations/5661455d-de5a-47ba-b99f-f6d50fdfc00b/", headers=user_token_headers
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Showtime has started"}
