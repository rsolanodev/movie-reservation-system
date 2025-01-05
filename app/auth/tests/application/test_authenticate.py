from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock, create_autospec

import jwt
import pytest
from freezegun import freeze_time

from app.auth.application.authenticate import Authenticate
from app.auth.domain.exceptions import (
    IncorrectPassword,
    UserDoesNotExist,
    UserInactive,
)
from app.settings import Settings
from app.shared.domain.finders.user_finder import UserFinder
from app.shared.tests.factories.user_factory_test import UserFactoryTest


class TestAuthenticate:
    @pytest.fixture
    def mock_user_finder(self) -> Any:
        return create_autospec(spec=UserFinder, instance=True, spec_set=True)

    @freeze_time("2021-08-01T12:00:00Z")
    def test_authenticate_user(self, mock_user_finder: Mock, settings: Settings) -> None:
        mock_user_finder.find_user_by_email.return_value = UserFactoryTest().create()

        token = Authenticate(finder=mock_user_finder).execute(email="rubensoljim@gmail.com", password="Passw0rd!")

        mock_user_finder.find_user_by_email.assert_called_once_with(email="rubensoljim@gmail.com")

        decoded_token = jwt.decode(token.access_token, key=settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded_token["sub"] == "913822a0-750b-4cb6-b7b9-e01869d7d62d"
        assert decoded_token["exp"] == datetime(2021, 8, 9, 12, 0, 0, tzinfo=timezone.utc).timestamp()

    def test_does_not_authenticate_user_when_password_is_incorrect(self, mock_user_finder: Mock) -> None:
        mock_user_finder.find_user_by_email.return_value = UserFactoryTest().create()

        with pytest.raises(IncorrectPassword):
            Authenticate(finder=mock_user_finder).execute(email="rubensoljim@gmail.com", password="Password!")

    def test_raises_exception_when_user_does_not_exist(self, mock_user_finder: Mock) -> None:
        mock_user_finder.find_user_by_email.return_value = None

        with pytest.raises(UserDoesNotExist):
            Authenticate(finder=mock_user_finder).execute(email="rubensoljim@gmail.com", password="Passw0rd!")

    def test_raises_exception_when_user_is_inactive(self, mock_user_finder: Mock) -> None:
        user = UserFactoryTest().create()
        user.mark_as_inactive()
        mock_user_finder.find_user_by_email.return_value = user

        with pytest.raises(UserInactive):
            Authenticate(finder=mock_user_finder).execute(email="rubensoljim@gmail.com", password="Passw0rd!")
