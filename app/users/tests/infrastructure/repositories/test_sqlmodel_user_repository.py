from sqlmodel import Session

from app.shared.infrastructure.repositories.sqlmodel_user_repository import (
    SqlModelUserRepository,
)
from app.shared.tests.factories.user_factory_test import UserFactoryTest
from app.users.infrastructure.models import UserModel


class TestSqlModelUserRepository:
    def test_create_user(self, session: Session) -> None:
        user = UserFactoryTest().create()
        SqlModelUserRepository(session=session).create(user=user)

        user_model = session.get_one(UserModel, user.id.to_uuid())
        assert user_model.to_domain() == user

    def test_find_user_by_email(self, session: Session) -> None:
        user_model = UserModel(
            email="rubensoljim@gmail.com",
            full_name="Rubén Solano",
            hashed_password="hashed_password",
        )
        session.add(user_model)

        user = SqlModelUserRepository(session=session).find_by_email(email="rubensoljim@gmail.com")

        assert user is not None
        assert user == user_model.to_domain()

    def test_find_user_by_email_returns_none(self, session: Session) -> None:
        user = SqlModelUserRepository(session=session).find_by_email(email="rubensoljim@hotmail.com")

        assert user is None
