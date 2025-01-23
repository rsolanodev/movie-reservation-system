from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.shared.domain.finders.user_finder import UserFinder
from app.shared.tests.domain.mothers.user_mother import UserMother
from app.users.application.commands.create_user import CreateUser, CreateUserParams
from app.users.domain.exceptions import UserAlreadyExists
from app.users.domain.repositories.user_repository import UserRepository


class TestCreateUser:
    @pytest.fixture
    def mock_user_repository(self) -> Any:
        return create_autospec(spec=UserRepository, instance=True, spec_set=True)

    @pytest.fixture
    def mock_user_finder(self) -> Any:
        return create_autospec(spec=UserFinder, instance=True, spec_set=True)

    def test_creates_user(self, mock_user_repository: Mock, mock_user_finder: Mock) -> None:
        mock_user_finder.find_user_by_email.return_value = None

        user = CreateUser(repository=mock_user_repository, finder=mock_user_finder).execute(
            params=CreateUserParams(
                email="rubensoljim@gmail.com",
                password="Passw0rd!",
                full_name="Rubén Solano",
            )
        )

        mock_user_finder.find_user_by_email.assert_called_once_with(email="rubensoljim@gmail.com")
        mock_user_repository.create.assert_called_once_with(user=user)

        assert user.verify_password("Passw0rd!")

    def test_raises_exception_when_user_already_exists(
        self, mock_user_repository: Mock, mock_user_finder: Mock
    ) -> None:
        mock_user_finder.find_user_by_email.return_value = UserMother().create()

        with pytest.raises(UserAlreadyExists):
            CreateUser(repository=mock_user_repository, finder=mock_user_finder).execute(
                params=CreateUserParams(
                    email="rubensoljim@gmail.com",
                    password="Passw0rd!",
                    full_name="Rubén Solano",
                )
            )
