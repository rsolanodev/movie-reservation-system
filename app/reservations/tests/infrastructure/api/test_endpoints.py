from collections.abc import Generator
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.reservations.application.create_reservation import CreateReservationParams
from app.reservations.domain.exceptions import SeatsNotAvailable
from app.users.infrastructure.models import UserModel


class TestCreateReservationEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.CreateReservation") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.SqlModelReservationRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_reservation_release_scheduler(self) -> Generator[Mock, None, None]:
        with patch("app.reservations.infrastructure.api.endpoints.CeleryReservationReleaseScheduler") as mock:
            yield mock.return_value

    def test_returns_201_and_calls_action(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
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

        mock_action.assert_called_once_with(
            repository=mock_repository,
            reservation_release_scheduler=mock_reservation_release_scheduler,
        )
        mock_action.return_value.execute.assert_called_once_with(
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
        mock_action: Mock,
        mock_repository: Mock,
        mock_reservation_release_scheduler: Mock,
        user_token_headers: dict[str, str],
        user: UserModel,
    ) -> None:
        mock_action.return_value.execute.side_effect = SeatsNotAvailable

        response = client.post(
            "api/v1/reservations/",
            json={
                "showtime_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "seat_ids": ["b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1"],
            },
            headers=user_token_headers,
        )

        mock_action.assert_called_once_with(
            repository=mock_repository,
            reservation_release_scheduler=mock_reservation_release_scheduler,
        )
        mock_action.return_value.execute.assert_called_once_with(
            params=CreateReservationParams(
                showtime_id=UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
                seat_ids=[UUID("b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1")],
                user_id=user.id,
            )
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Seats not available"}

    def test_returns_401_when_user_is_not_authenticated(
        self, client: TestClient, mock_action: Mock, mock_repository: Mock
    ) -> None:
        response = client.post(
            "api/v1/reservations/",
            json={
                "showtime_id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
                "seat_ids": ["b0ed1c31-9877-4d05-bb1c-0c1385ae4fd1"],
            },
        )

        mock_action.assert_not_called()
        mock_repository.assert_not_called()

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}
