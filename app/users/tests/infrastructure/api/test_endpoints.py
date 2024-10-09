from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.users.actions.create_user import CreateUserParams
from app.users.domain.exceptions import UserAlreadyExistsException
from app.users.tests.factories.user_factory import UserFactory


class TestCreateUserEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.users.infrastructure.api.endpoints.CreateUser") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch("app.users.infrastructure.api.endpoints.SqlModelUserRepository") as mock:
            yield mock.return_value

    def test_returns_201_and_calls_action_and_returns_result(
        self, client: TestClient, mock_action: Mock, mock_repository: Mock
    ) -> None:
        mock_action.return_value.execute.return_value = UserFactory().create()

        response = client.post(
            "api/v1/users/",
            json={
                "email": "rubensoljim@gmail.com",
                "password": "Passw0rd!",
                "full_name": "Rubén Solano",
            },
        )

        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            params=CreateUserParams(
                email="rubensoljim@gmail.com",
                password="Passw0rd!",
                full_name="Rubén Solano",
            ),
        )

        assert response.status_code == 201
        assert response.json() == {
            "id": "913822a0-750b-4cb6-b7b9-e01869d7d62d",
            "email": "rubensoljim@gmail.com",
            "full_name": "Rubén Solano",
            "is_active": True,
            "is_superuser": False,
        }

    def test_returns_400_when_user_already_exists(self, client: TestClient, mock_action: Mock) -> None:
        mock_action.return_value.execute.side_effect = UserAlreadyExistsException

        response = client.post(
            "api/v1/users/",
            json={
                "email": "rubensoljim@gmail.com",
                "password": "Passw0rd!",
                "full_name": "Rubén Solano",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "The user with this email already exists"
