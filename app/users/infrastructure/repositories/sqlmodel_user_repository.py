from app.shared.domain.user import User
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository
from app.users.domain.repositories.user_repository import UserRepository
from app.users.infrastructure.models import UserModel


class SqlModelUserRepository(UserRepository, SqlModelRepository):
    def create(self, user: User) -> None:
        user_model = UserModel.from_domain(user=user)
        self._session.add(user_model)
        self._session.commit()
