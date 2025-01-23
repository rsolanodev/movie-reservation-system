from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.tests.infrastructure.builders.sqlmodel_movie_builder import SqlModelMovieBuilder
from app.shared.tests.infrastructure.mothers.sqlmodel_room_mother import SqlModelRoomMother
from app.shared.tests.infrastructure.mothers.sqlmodel_showtime_mother import SqlModelShowtimeMother
from app.showtimes.application.commands.create_showtime import CreateShowtimeParams
from app.showtimes.domain.exceptions import ShowtimeAlreadyExists
from app.showtimes.domain.seat import Seat, SeatStatus
from app.showtimes.infrastructure.models import ShowtimeModel
from app.showtimes.tests.infrastructure.mothers.sqlmodel_seat_mother import SqlModelSeatMother


class TestCreateShowtimeEndpoint:
    @pytest.fixture
    def mock_create_showtime(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.CreateShowtime") as mock:
            yield mock

    @pytest.fixture
    def mock_showtime_repository(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.SqlModelShowtimeRepository") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, session: Session, client: TestClient, superuser_token_headers: dict[str, str]) -> None:
        SqlModelRoomMother(session).create()

        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "room_id": "fbdd7b54-c561-4cbb-a55f-15853c60e600",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
            headers=superuser_token_headers,
        )

        assert response.status_code == 201

        showtime_model = session.exec(select(ShowtimeModel)).one()
        assert showtime_model.movie_id == UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        assert showtime_model.room_id == UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600")
        assert showtime_model.show_datetime == datetime(2022, 8, 10, 22, 0, 0)

    def test_returns_201_and_calls_create_showtime(
        self,
        client: TestClient,
        mock_create_showtime: Mock,
        mock_showtime_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "room_id": "fbdd7b54-c561-4cbb-a55f-15853c60e600",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
            headers=superuser_token_headers,
        )

        mock_create_showtime.assert_called_once_with(repository=mock_showtime_repository)
        mock_create_showtime.return_value.execute.assert_called_once_with(
            params=CreateShowtimeParams(
                movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                room_id=Id("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=DateTime.from_datetime(datetime(2022, 8, 10, 22, 0, 0)),
            )
        )

        assert response.status_code == 201

    def test_returns_400_when_showtime_already_exists(
        self,
        client: TestClient,
        mock_create_showtime: Mock,
        mock_showtime_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_create_showtime.return_value.execute.side_effect = ShowtimeAlreadyExists

        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "room_id": "fbdd7b54-c561-4cbb-a55f-15853c60e600",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
            headers=superuser_token_headers,
        )

        mock_create_showtime.assert_called_once_with(repository=mock_showtime_repository)
        mock_create_showtime.return_value.execute.assert_called_once_with(
            params=CreateShowtimeParams(
                movie_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                room_id=Id("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=DateTime.from_datetime(datetime(2022, 8, 10, 22, 0, 0)),
            )
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Showtime for movie already exists"}

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_create_showtime: Mock,
        mock_showtime_repository: Mock,
    ) -> None:
        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "room_id": "fbdd7b54-c561-4cbb-a55f-15853c60e600",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
        )

        mock_create_showtime.assert_not_called()
        mock_showtime_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_create_showtime: Mock,
        mock_showtime_repository: Mock,
        user_token_headers: dict[str, str],
    ) -> None:
        response = client.post(
            "api/v1/showtimes/",
            json={
                "movie_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "room_id": "fbdd7b54-c561-4cbb-a55f-15853c60e600",
                "show_datetime": "2022-08-10T22:00:00Z",
            },
            headers=user_token_headers,
        )

        mock_create_showtime.assert_not_called()
        mock_showtime_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestDeleteShowtimeEndpoint:
    @pytest.fixture
    def mock_delete_showtime(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.DeleteShowtime") as mock:
            yield mock

    @pytest.fixture
    def mock_showtime_repository(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.SqlModelShowtimeRepository") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, session: Session, client: TestClient, superuser_token_headers: dict[str, str]) -> None:
        showtime_model = SqlModelShowtimeMother(session).create()

        response = client.delete(
            "api/v1/showtimes/cbdd7b54-c561-4cbb-a55f-15853c60e600/",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        assert session.get(ShowtimeModel, showtime_model.id) is None

    def test_returns_200_and_calls_delete_showtime(
        self,
        client: TestClient,
        mock_delete_showtime: Mock,
        mock_showtime_repository: Mock,
        superuser_token_headers: dict[str, str],
    ) -> None:
        mock_delete_showtime.return_value.execute.return_value = None

        response = client.delete(
            "api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=superuser_token_headers,
        )

        mock_delete_showtime.assert_called_once_with(repository=mock_showtime_repository)
        mock_delete_showtime.return_value.execute.assert_called_once_with(
            showtime_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )

        assert response.status_code == 200

    def test_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        mock_delete_showtime: Mock,
        mock_showtime_repository: Mock,
    ) -> None:
        response = client.delete(
            "api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
        )

        mock_delete_showtime.assert_not_called()
        mock_showtime_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_returns_403_when_user_is_not_superuser(
        self,
        client: TestClient,
        mock_delete_showtime: Mock,
        mock_showtime_repository: Mock,
        user_token_headers: dict[str, str],
    ) -> None:
        response = client.delete(
            "api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/",
            headers=user_token_headers,
        )

        mock_delete_showtime.assert_not_called()
        mock_showtime_repository.assert_not_called()

        assert response.status_code == 403
        assert response.json() == {"detail": "The user doesn't have enough privileges"}


class TestListSeatsEndpoint:
    @pytest.fixture
    def mock_find_seats(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.FindSeats") as mock:
            yield mock

    @pytest.fixture
    def mock_seat_finder(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.SqlModelSeatFinder") as mock:
            yield mock.return_value

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "status", [SeatStatus.AVAILABLE.value, SeatStatus.RESERVED.value, SeatStatus.OCCUPIED.value]
    )
    def test_integration(self, session: Session, client: TestClient, status: SeatStatus) -> None:
        showtime_id = UUID("39ce0103-fe6d-4bc4-a876-1556e9291bbe")
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
            .with_id(UUID("7846b1f9-218e-4c67-bc65-0e870be65a07"))
            .with_showtime_id(showtime_id)
            .with_row(1)
            .with_number(2)
            .with_status(status)
            .create()
        )
        SqlModelSeatMother(session).with_row(1).with_number(1).create()

        response = client.get(f"api/v1/showtimes/{showtime_id}/seats/")

        assert response.status_code == 200
        assert response.json() == [
            {"id": "7846b1f9-218e-4c67-bc65-0e870be65a07", "row": 1, "number": 2, "status": status}
        ]

    @pytest.mark.parametrize("status", [SeatStatus.AVAILABLE, SeatStatus.RESERVED, SeatStatus.OCCUPIED])
    def test_returns_200_and_calls_find_seats(
        self, client: TestClient, mock_find_seats: Mock, mock_seat_finder: Mock, status: SeatStatus
    ) -> None:
        mock_find_seats.return_value.execute.return_value = [
            Seat(id=Id("cbdd7b54-c561-4cbb-a55f-15853c60e600"), row=1, number=2, status=status),
        ]

        response = client.get("api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/seats/")

        mock_find_seats.assert_called_once_with(finder=mock_seat_finder)
        mock_find_seats.return_value.execute.assert_called_once_with(
            showtime_id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )

        assert response.status_code == 200
        assert response.json() == [
            {"id": "cbdd7b54-c561-4cbb-a55f-15853c60e600", "row": 1, "number": 2, "status": status}
        ]
