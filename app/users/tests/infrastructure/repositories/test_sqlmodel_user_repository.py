from sqlmodel import Session

from app.shared.tests.domain.mothers.user_mother import UserMother
from app.users.infrastructure.models import UserModel
from app.users.infrastructure.repositories.sqlmodel_user_repository import SqlModelUserRepository


class TestSqlModelUserRepository:
    def test_create_user(self, session: Session) -> None:
        user = UserMother().create()
        SqlModelUserRepository(session).create(user=user)

        user_model = session.get_one(UserModel, user.id.to_uuid())
        assert user_model.to_domain() == user
