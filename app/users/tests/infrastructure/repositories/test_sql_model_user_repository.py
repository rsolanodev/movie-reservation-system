from sqlmodel import Session

from app.users.infrastructure.models import UserModel
from app.users.infrastructure.repositories.sql_model_user_repository import (
    SqlModelUserRepository,
)
from app.users.tests.factories.user_factory import UserFactory


class TestSqlModelUserRepository:
    def test_create(self, session: Session) -> None:
        user = UserFactory().create()
        SqlModelUserRepository(session=session).create(user=user)

        user_model = session.get(UserModel, user.id)
        assert user_model is not None
        assert user_model.to_domain() == user

    def test_find_by_email(self, session: Session) -> None:
        user_model = UserModel(
            email="rubensoljim@gmail.com",
            full_name="Rubén Solano",
            hashed_password="hashed_password",
        )
        session.add(user_model)
        session.commit()

        user = SqlModelUserRepository(session=session).find_by_email(
            email="rubensoljim@gmail.com"
        )

        assert user is not None
        assert user == user_model.to_domain()

    def test_find_by_email_returns_none(self, session: Session) -> None:
        user = SqlModelUserRepository(session=session).find_by_email(
            email="rubensoljim@hotmail.com"
        )

        assert user is None
