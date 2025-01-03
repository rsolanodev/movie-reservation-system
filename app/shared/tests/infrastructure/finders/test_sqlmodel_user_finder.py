from sqlmodel import Session

from app.shared.infrastructure.finders.sqlmodel_user_finder import SqlModelUserFinder
from app.users.infrastructure.models import UserModel


class TestSqlModelUserFinder:
    def test_find_user_by_email(self, session: Session) -> None:
        user_model = UserModel(
            email="rubensoljim@gmail.com",
            full_name="Rubén Solano",
            hashed_password="hashed_password",
        )
        session.add(user_model)

        user = SqlModelUserFinder(session=session).find_user_by_email(email="rubensoljim@gmail.com")

        assert user is not None
        assert user == user_model.to_domain()

    def test_does_not_find_user_by_email_when_it_does_not_exist(self, session: Session) -> None:
        user = SqlModelUserFinder(session=session).find_user_by_email(email="rubensoljim@hotmail.com")

        assert user is None
