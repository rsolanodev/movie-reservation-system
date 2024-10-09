from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.auth.application.authenticate import Authenticate
from app.auth.domain.entities import Token
from app.auth.domain.exceptions import (
    IncorrectPasswordException,
    UserDoesNotExistException,
    UserInactiveException,
)
from app.auth.infrastructure.responses import TokenResponse
from app.users.infrastructure.repositories.sql_model_user_repository import (
    SqlModelUserRepository,
)

router = APIRouter()


@router.post("/access-token/", response_model=TokenResponse)
def authenticate_user(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    try:
        token = Authenticate(repository=SqlModelUserRepository(session=session)).execute(
            email=form_data.username,
            password=form_data.password,
        )
    except (UserDoesNotExistException, IncorrectPasswordException):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    except UserInactiveException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return token
