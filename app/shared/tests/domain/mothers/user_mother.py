from app.shared.domain.user import User
from app.shared.domain.value_objects.id import Id


class UserMother:
    def __init__(self) -> None:
        self._user = User(
            id=Id("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            email="rubensoljim@gmail.com",
            full_name="Rubén Solano",
            hashed_password="$2b$12$ZurDA9.M2DapH/p9Q.s6WeoboRPCamp3MbZczwMxyNZ0Z.16.vckm",
            is_active=True,
            is_superuser=False,
        )

    def superuser(self) -> "UserMother":
        self._user.is_superuser = True
        return self

    def create(self) -> User:
        return self._user
