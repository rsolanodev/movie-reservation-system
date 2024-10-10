import uuid

from app.users.domain.user import User


class UserFactory:
    def create(self, is_superuser: bool = False) -> User:
        return User(
            id=uuid.UUID("913822a0-750b-4cb6-b7b9-e01869d7d62d"),
            email="rubensoljim@gmail.com",
            full_name="Rubén Solano",
            hashed_password="$2b$12$ZurDA9.M2DapH/p9Q.s6WeoboRPCamp3MbZczwMxyNZ0Z.16.vckm",
            is_active=True,
            is_superuser=is_superuser,
        )
