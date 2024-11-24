from collections.abc import Generator
from unittest.mock import ANY, Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.auth.domain.exceptions import (
    IncorrectPassword,
    UserDoesNotExist,
    UserInactive,
)
from app.auth.domain.token import Token, TokenType


class TestAuthenticateUserEndpoint:
    @pytest.fixture
    def mock_authenticate(self) -> Generator[Mock, None, None]:
        with patch("app.auth.infrastructure.api.endpoints.Authenticate") as mock:
            yield mock

    @pytest.fixture
    def mock_user_repository(self) -> Generator[Mock, None, None]:
        with patch("app.auth.infrastructure.api.endpoints.SqlModelUserRepository") as mock:
            yield mock.return_value

    @pytest.mark.integration
    @pytest.mark.usefixtures("user")
    def test_integration(self, client: TestClient) -> None:
        response = client.post(
            "api/v1/auth/access-token/",
            data={
                "username": "rubensoljim@gmail.com",
                "password": "Passw0rd!",
            },
        )

        assert response.status_code == 200
        assert response.json() == {"token_type": "bearer", "access_token": ANY, "expires_in": 11520}

    def test_calls_authenticate_and_returns_access_token(
        self, client: TestClient, mock_authenticate: Mock, mock_user_repository: Mock
    ) -> None:
        mock_authenticate.return_value.execute.return_value = Token(
            access_token="access_token",
            token_type=TokenType.BEARER,
            expires_in=86400,
        )
        response = client.post(
            "api/v1/auth/access-token/",
            data={
                "username": "rubensoljim@gmail.com",
                "password": "Passw0rd!",
            },
        )
        mock_authenticate.assert_called_once_with(repository=mock_user_repository)
        mock_authenticate.return_value.execute.assert_called_once_with(
            email="rubensoljim@gmail.com", password="Passw0rd!"
        )
        assert response.status_code == 200
        assert response.json() == {
            "token_type": "bearer",
            "access_token": "access_token",
            "expires_in": 86400,
        }

    @pytest.mark.parametrize("expected_exception", [UserDoesNotExist, IncorrectPassword])
    def test_returns_400_when_is_incorrect_email_or_password(
        self, client: TestClient, mock_authenticate: Mock, expected_exception: Exception
    ) -> None:
        mock_authenticate.return_value.execute.side_effect = expected_exception

        response = client.post(
            "api/v1/auth/access-token/",
            data={
                "username": "rsolanodev",
                "password": "Passw0rd!",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Incorrect email or password"

    def test_returns_400_when_user_is_inactive(self, client: TestClient, mock_authenticate: Mock) -> None:
        mock_authenticate.return_value.execute.side_effect = UserInactive

        response = client.post(
            "api/v1/auth/access-token/",
            data={
                "username": "rsolanodev",
                "password": "Passw0rd!",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Inactive user"
