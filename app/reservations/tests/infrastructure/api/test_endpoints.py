from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.reservations.application.create_reservation import CreateReservationParams
from app.reservations.domain.exceptions import SeatsNotAvailable
from app.reservations.domain.movie_reservation import Movie, MovieReservation, ReservedSeat
from app.reservations.domain.seat import SeatStatus
from app.reservations.tests.builders.sqlmodel_reservation_builder_test import SqlModelReservationBuilderTest
from app.reservations.tests.builders.sqlmodel_seat_builder_test import SqlModelSeatBuilderTest
from app.reservations.tests.factories.sqlmodel_seat_factory_test import SqlModelSeatFactoryTest
from app.shared.tests.builders.sqlmodel_movie_builder_test import SqlModelMovieBuilderTest
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

    @pytest.fixture(autouse=True)
    def mock_reservation_release_scheduler(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.CeleryReservationReleaseScheduler") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(
        self, session: Session, client: TestClient, user_token_headers: dict[str, str], user: UserModel
    ) -> None:
        seat = SqlModelSeatFactoryTest(session).create_available()

        response = client.post(
            "api/v1/reservations/",
            json={"showtime_id": str(seat.showtime_id), "seat_ids": [str(seat.id)]},
            headers=user_token_headers,
        )

        assert response.status_code == 201

        session.refresh(seat)
        assert seat.status == SeatStatus.RESERVED
        assert seat.reservation_id is not None
        assert seat.reservation.user_id == user.id

    def test_returns_201_and_calls_create_reservation(
        self,
        client: TestClient,
        mock_create_reservation: Mock,
        mock_reservation_repository: Mock,
        mock_reservation_release_scheduler: Mock,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
        response = client.post(
            "api/v1/reservations/",
            json={
                "showtime_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "seat_ids": ["b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1"],
            },
            headers=user_token_headers,
        )

        mock_create_reservation.assert_called_once_with(
            repository=mock_reservation_repository,
            reservation_release_scheduler=mock_reservation_release_scheduler,
        )
        mock_create_reservation.return_value.execute.assert_called_once_with(
            params=CreateReservationParams(
                showtime_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                seat_ids=[UUID("b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1")],
                user_id=user.id,
            )
        )

        assert response.status_code == 201

    def test_returns_400_when_seats_not_available(
        self,
        client: TestClient,
        mock_create_reservation: Mock,
        mock_reservation_repository: Mock,
        mock_reservation_release_scheduler: Mock,
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
            repository=mock_reservation_repository,
            reservation_release_scheduler=mock_reservation_release_scheduler,
        )
        mock_create_reservation.return_value.execute.assert_called_once_with(
            params=CreateReservationParams(
                showtime_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                seat_ids=[UUID("b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1")],
                user_id=user.id,
            )
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Seats not available"}

    def test_returns_401_when_user_is_not_authenticated(
        self, client: TestClient, mock_create_reservation: Mock, mock_reservation_repository: Mock
    ) -> None:
        response = client.post(
            "api/v1/reservations/",
            json={
                "showtime_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "seat_ids": ["b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1"],
            },
        )

        mock_create_reservation.assert_not_called()
        mock_reservation_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


class TestRetrieveReservationsEndpoint:
    @pytest.fixture
    def mock_retrieve_reservations(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.RetrieveReservations") as mock:
            yield mock

    @pytest.fixture
    def mock_reservation_repository(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.SqlModelReservationRepository") as mock:
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
            .with_user_id(user.id)
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

    def test_returns_200_and_calls_retrieve_reservations(
        self,
        client: TestClient,
        mock_retrieve_reservations: Mock,
        mock_reservation_repository: Mock,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
        mock_retrieve_reservations.return_value.execute.return_value = [
            MovieReservation(
                reservation_id=UUID("5661455d-de5a-47ba-b99f-f6d50fdfc00b"),
                show_datetime=datetime(2024, 1, 2, 22, 0, tzinfo=timezone.utc),
                movie=Movie(
                    id=UUID("d64a9a87-4484-46f9-8ec1-f1e1c9fe2880"),
                    title="Robot Salvaje",
                    poster_image="robot_salvaje.jpg",
                ),
                seats=[ReservedSeat(row=1, number=2)],
            ),
            MovieReservation(
                reservation_id=UUID("ffd7e9f4-bec7-4487-8f2f-d84b49d0bcee"),
                show_datetime=datetime(2024, 1, 1, 20, 0, tzinfo=timezone.utc),
                movie=Movie(
                    id=UUID("6c42605f-ac4a-405d-94f2-1f0ea3de5ddb"),
                    title="La Sustancia",
                    poster_image="la_sustancia.jpg",
                ),
                seats=[ReservedSeat(row=3, number=4)],
            ),
        ]

        response = client.get("api/v1/reservations/", headers=user_token_headers)

        mock_retrieve_reservations.assert_called_once_with(repository=mock_reservation_repository)
        mock_retrieve_reservations.return_value.execute.assert_called_once_with(user_id=user.id)

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
        self, client: TestClient, mock_retrieve_reservations: Mock, mock_reservation_repository: Mock
    ) -> None:
        response = client.get("api/v1/reservations/")

        mock_retrieve_reservations.assert_not_called()
        mock_reservation_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}