from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.auth.domain.entities import Token, TokenType
from app.auth.domain.exceptions import (
    IncorrectPasswordException,
    UserDoesNotExistException,
    UserInactiveException,
)


class TestAuthenticateUserEndpoint:
    @pytest.fixture
    def mock_action(self) -> Generator[Mock, None, None]:
        with patch("app.auth.infrastructure.api.endpoints.Authenticate") as mock:
            yield mock

    @pytest.fixture
    def mock_repository(self) -> Generator[Mock, None, None]:
        with patch(
            "app.auth.infrastructure.api.endpoints.SqlModelUserRepository"
        ) as mock:
            yield mock.return_value

    def test_calls_action_and_returns_access_token(
        self,
        client: TestClient,
        mock_action: Mock,
        mock_repository: Mock,
    ) -> None:
        mock_action.return_value.execute.return_value = Token(
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
        mock_action.assert_called_once_with(repository=mock_repository)
        mock_action.return_value.execute.assert_called_once_with(
            email="rubensoljim@gmail.com", password="Passw0rd!"
        )
        assert response.status_code == 200
        assert response.json() == {
            "token_type": "bearer",
            "access_token": "access_token",
            "expires_in": 86400,
        }

    @pytest.mark.parametrize(
        "expected_exception", [UserDoesNotExistException, IncorrectPasswordException]
    )
    def test_returns_400_when_is_incorrect_email_or_password(
        self, client: TestClient, mock_action: Mock, expected_exception: Exception
    ) -> None:
        mock_action.return_value.execute.side_effect = expected_exception
        response = client.post(
            "api/v1/auth/access-token/",
            data={
                "username": "rsolanodev",
                "password": "Passw0rd!",
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Incorrect email or password"

    def test_returns_400_when_user_is_inactive(
        self, client: TestClient, mock_action: Mock
    ) -> None:
        mock_action.return_value.execute.side_effect = UserInactiveException
        response = client.post(
            "api/v1/auth/access-token/",
            data={
                "username": "rsolanodev",
                "password": "Passw0rd!",
            },
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Inactive user"
