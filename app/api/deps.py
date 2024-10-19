from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, security, status
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session

from app.database import get_db_session
from app.settings import settings
from app.users.infrastructure.models import UserModel

SessionDep = Annotated[Session, Depends(get_db_session)]

reusable_oauth2 = security.OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/access-token/")
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> UserModel:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(UserModel, UUID(payload.get("sub")))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[UserModel, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> UserModel:
    if current_user.is_superuser is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
