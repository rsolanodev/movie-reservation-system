from sqlmodel import Session

from app.shared.tests.factories.user_factory_test import UserFactoryTest
from app.users.infrastructure.models import UserModel
from app.users.infrastructure.repositories.sqlmodel_user_repository import SqlModelUserRepository


class TestSqlModelUserRepository:
    def test_create_user(self, session: Session) -> None:
        user = UserFactoryTest().create()
        SqlModelUserRepository(session=session).create(user=user)

        user_model = session.get_one(UserModel, user.id.to_uuid())
        assert user_model.to_domain() == user
