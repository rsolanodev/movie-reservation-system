from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.auth.application.authenticate import Authenticate
from app.auth.domain.exceptions import (
    IncorrectPassword,
    UserDoesNotExist,
    UserInactive,
)
from app.auth.infrastructure.responses import TokenResponse
from app.shared.infrastructure.finders.sqlmodel_user_finder import SqlModelUserFinder

router = APIRouter()


@router.post("/access-token/", response_model=TokenResponse)
def authenticate_user(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenResponse:
    try:
        token = Authenticate(finder=SqlModelUserFinder(session=session)).execute(
            email=form_data.username, password=form_data.password
        )
    except (UserDoesNotExist, IncorrectPassword):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    except UserInactive:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return TokenResponse.from_domain(token)
