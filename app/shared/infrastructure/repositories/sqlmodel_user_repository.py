from sqlmodel import select

from app.shared.domain.repositories.user_repository import UserRepository
from app.shared.domain.user import User
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository
from app.users.infrastructure.models import UserModel


class SqlModelUserRepository(UserRepository, SqlModelRepository):
    def create(self, user: User) -> None:
        user_model = UserModel.from_domain(user=user)
        self._session.add(user_model)
        self._session.commit()

    def find_by_email(self, email: str) -> User | None:
        statement = select(UserModel).where(UserModel.email == email)
        user_model = self._session.exec(statement).first()

        return user_model.to_domain() if user_model else None
