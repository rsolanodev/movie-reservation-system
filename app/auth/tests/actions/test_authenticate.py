from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock, create_autospec

import jwt
import pytest
from freezegun import freeze_time

from app.auth.actions.authenticate import Authenticate
from app.auth.domain.exceptions import (
    IncorrectPasswordException,
    UserDoesNotExistException,
    UserInactiveException,
)
from app.settings import settings
from app.users.domain.repositories.user_repository import UserRepository
from app.users.tests.factories.user_factory import UserFactory


class TestAuthenticate:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(UserRepository, instance=True)

    @freeze_time("2021-08-01T12:00:00Z")
    def test_authenticate_user(self, mock_repository: Mock) -> None:
        mock_repository.find_by_email.return_value = UserFactory().create()

        token = Authenticate(repository=mock_repository).execute(email="rubensoljim@gmail.com", password="Passw0rd!")

        mock_repository.find_by_email.assert_called_once_with(email="rubensoljim@gmail.com")

        decoded_token = jwt.decode(token.access_token, key=settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded_token["sub"] == "913822a0-750b-4cb6-b7b9-e01869d7d62d"
        assert decoded_token["exp"] == datetime(2021, 8, 9, 12, 0, 0, tzinfo=timezone.utc).timestamp()

    def test_does_not_authenticate_user_when_password_is_incorrect(self, mock_repository: Mock) -> None:
        mock_repository.find_by_email.return_value = UserFactory().create()

        with pytest.raises(IncorrectPasswordException):
            Authenticate(repository=mock_repository).execute(email="rubensoljim@gmail.com", password="Password!")

    def test_raises_exception_when_user_does_not_exist(self, mock_repository: Mock) -> None:
        mock_repository.find_by_email.return_value = None

        with pytest.raises(UserDoesNotExistException):
            Authenticate(repository=mock_repository).execute(email="rubensoljim@gmail.com", password="Passw0rd!")

    def test_raises_exception_when_user_is_inactive(self, mock_repository: Mock) -> None:
        user = UserFactory().create()
        user.mark_as_inactive()
        mock_repository.find_by_email.return_value = user

        with pytest.raises(UserInactiveException):
            Authenticate(repository=mock_repository).execute(email="rubensoljim@gmail.com", password="Passw0rd!")
