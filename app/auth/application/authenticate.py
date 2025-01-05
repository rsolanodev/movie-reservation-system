from app.auth.domain.exceptions import IncorrectPassword, UserDoesNotExist, UserInactive
from app.auth.domain.token import Token
from app.settings import get_settings
from app.shared.domain.finders.user_finder import UserFinder

settings = get_settings()


class Authenticate:
    def __init__(self, finder: UserFinder) -> None:
        self._finder = finder

    def execute(self, email: str, password: str) -> Token:
        user = self._finder.find_user_by_email(email=email)

        if user is None:
            raise UserDoesNotExist()

        if user.verify_password(password) is False:
            raise IncorrectPassword()

        if user.is_active is False:
            raise UserInactive()

        return Token.create(
            user_id=user.id,
            secret_key=settings.SECRET_KEY,
            expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
