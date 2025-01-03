from sqlmodel import select

from app.shared.domain.finders.user_finder import UserFinder
from app.shared.domain.user import User
from app.shared.infrastructure.finders.sqlmodel_finder import SqlModelFinder
from app.users.infrastructure.models import UserModel


class SqlModelUserFinder(UserFinder, SqlModelFinder):
    def find_user_by_email(self, email: str) -> User | None:
        statement = select(UserModel).where(UserModel.email == email)
        user_model = self._session.exec(statement).first()

        return user_model.to_domain() if user_model else None
