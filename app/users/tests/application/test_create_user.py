from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.users.application.create_user import CreateUser, CreateUserParams
from app.users.domain.exceptions import UserAlreadyExistsException
from app.users.domain.repositories.user_repository import (
    UserRepository,
)
from app.users.tests.factories.user_factory import UserFactory


class TestCreateUser:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(UserRepository, instance=True)

    def test_creates_user(self, mock_repository: Mock) -> None:
        mock_repository.find_by_email.return_value = None

        user = CreateUser(repository=mock_repository).execute(
            params=CreateUserParams(
                email="rubensoljim@gmail.com",
                password="Passw0rd!",
                full_name="Rubén Solano",
            )
        )

        mock_repository.find_by_email.assert_called_once_with(email="rubensoljim@gmail.com")
        mock_repository.create.assert_called_once_with(user=user)

        assert user.verify_password("Passw0rd!")

    def test_raises_exception_when_user_already_exists(self, mock_repository: Mock) -> None:
        mock_repository.find_by_email.return_value = UserFactory().create()

        with pytest.raises(UserAlreadyExistsException):
            CreateUser(repository=mock_repository).execute(
                params=CreateUserParams(
                    email="rubensoljim@gmail.com",
                    password="Passw0rd!",
                    full_name="Rubén Solano",
                )
            )
