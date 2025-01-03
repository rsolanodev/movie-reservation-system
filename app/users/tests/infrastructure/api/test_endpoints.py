from collections.abc import Generator
from unittest.mock import ANY, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.shared.tests.factories.user_factory_test import UserFactoryTest
from app.users.application.create_user import CreateUserParams
from app.users.domain.exceptions import UserAlreadyExists


class TestCreateUserEndpoint:
    @pytest.fixture
    def mock_create_user(self) -> Generator[Mock, None, None]:
        with patch("app.users.infrastructure.api.endpoints.CreateUser") as mock:
            yield mock

    @pytest.fixture
    def mock_user_repository(self) -> Generator[Mock, None, None]:
        with patch("app.users.infrastructure.api.endpoints.SqlModelUserRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_user_finder(self) -> Generator[Mock, None, None]:
        with patch("app.users.infrastructure.api.endpoints.SqlModelUserFinder") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, client: TestClient) -> None:
        response = client.post(
            "api/v1/users/",
            json={
                "email": "rubensoljim@gmail.com",
                "password": "Passw0rd!",
                "full_name": "Rubén Solano",
            },
        )

        assert response.status_code == 201
        assert response.json() == {
            "id": ANY,
            "email": "rubensoljim@gmail.com",
            "full_name": "Rubén Solano",
            "is_active": True,
            "is_superuser": False,
        }

    def test_returns_201_and_calls_create_user(
        self, client: TestClient, mock_create_user: Mock, mock_user_repository: Mock, mock_user_finder: Mock
    ) -> None:
        mock_create_user.return_value.execute.return_value = UserFactoryTest().create()

        response = client.post(
            "api/v1/users/",
            json={
                "email": "rubensoljim@gmail.com",
                "password": "Passw0rd!",
                "full_name": "Rubén Solano",
            },
        )

        mock_create_user.assert_called_once_with(repository=mock_user_repository, finder=mock_user_finder)
        mock_create_user.return_value.execute.assert_called_once_with(
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

    def test_returns_400_when_user_already_exists(self, client: TestClient, mock_create_user: Mock) -> None:
        mock_create_user.return_value.execute.side_effect = UserAlreadyExists

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
