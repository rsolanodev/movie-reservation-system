from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.shared.tests.builders.sqlmodel_movie_builder_test import SqlModelMovieBuilderTest
from app.shared.tests.factories.sqlmodel_room_factory_test import SqlModelRoomFactoryTest
from app.showtimes.application.create_showtime import CreateShowtimeParams
from app.showtimes.domain.exceptions import ShowtimeAlreadyExists
from app.showtimes.domain.seat import Seat, SeatStatus
from app.showtimes.infrastructure.models import ShowtimeModel
from app.showtimes.tests.factories.sqlmodel_seat_factory_test import SqlModelSeatFactoryTest
from app.showtimes.tests.factories.sqlmodel_showtime_factory_test import SqlModelShowtimeFactoryTest


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
        SqlModelRoomFactoryTest(session=session).create(
            id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"), name="Room 1", seat_configuration=[{"row": 1, "number": 2}]
        )

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

        showtime_model = session.exec(select(ShowtimeModel)).first()
        assert showtime_model is not None
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
                movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2022, 8, 10, 22, 0, 0, tzinfo=timezone.utc),
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
                movie_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
                show_datetime=datetime(2022, 8, 10, 22, 0, 0, tzinfo=timezone.utc),
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
        showtime_model = SqlModelShowtimeFactoryTest(session=session).create(
            id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"),
            show_datetime=datetime(2023, 4, 1, 20, 0, tzinfo=timezone.utc),
        )

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
            showtime_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
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


class TestRetrieveSeatsEndpoint:
    @pytest.fixture
    def mock_retrieve_seats(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.RetrieveSeats") as mock:
            yield mock

    @pytest.fixture
    def mock_showtime_repository(self) -> Generator[Mock, None, None]:
        with patch("app.showtimes.infrastructure.api.endpoints.SqlModelShowtimeRepository") as mock:
            yield mock.return_value

    @pytest.mark.integration
    @pytest.mark.parametrize("status", [SeatStatus.AVAILABLE, SeatStatus.RESERVED, SeatStatus.OCCUPIED])
    def test_integration(self, session: Session, client: TestClient, status: SeatStatus) -> None:
        showtime_id = UUID("cbdd7b54-c561-4cbb-a55f-15853c60e601")

        SqlModelMovieBuilderTest(session=session).with_id(
            id=UUID("ec725625-f502-4d39-9401-a415d8c1f964")
        ).with_showtime(
            id=showtime_id,
            show_datetime=datetime(2023, 4, 3, 22, 0, tzinfo=timezone.utc),
            room_id=UUID("fbdd7b54-c561-4cbb-a55f-15853c60e600"),
        ).build()

        seat_model_factory = SqlModelSeatFactoryTest(session=session)
        seat_model_expected = seat_model_factory.create(showtime_id=showtime_id, row=1, number=2, status=status)
        seat_model_factory.create(row=1, number=1)

        response = client.get(f"api/v1/showtimes/{showtime_id}/seats/")

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": str(seat_model_expected.id),
                "row": seat_model_expected.row,
                "number": seat_model_expected.number,
                "status": seat_model_expected.status,
            }
        ]

    @pytest.mark.parametrize("status", [SeatStatus.AVAILABLE, SeatStatus.RESERVED, SeatStatus.OCCUPIED])
    def test_returns_200_and_calls_retrieve_seats(
        self, client: TestClient, mock_retrieve_seats: Mock, mock_showtime_repository: Mock, status: SeatStatus
    ) -> None:
        mock_retrieve_seats.return_value.execute.return_value = [
            Seat(id=UUID("cbdd7b54-c561-4cbb-a55f-15853c60e600"), row=1, number=2, status=status),
        ]

        response = client.get("api/v1/showtimes/913822a0-750b-4cb6-b7b9-e01869d7d62d/seats/")

        mock_retrieve_seats.assert_called_once_with(repository=mock_showtime_repository)
        mock_retrieve_seats.return_value.execute.assert_called_once_with(
            showtime_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d")
        )

        assert response.status_code == 200
        assert response.json() == [
            {"id": "cbdd7b54-c561-4cbb-a55f-15853c60e600", "row": 1, "number": 2, "status": status}
        ]
