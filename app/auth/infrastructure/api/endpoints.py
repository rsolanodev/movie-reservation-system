from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.auth.actions.authenticate import Authenticate
from app.auth.domain.exceptions import (
    IncorrectPasswordException,
    UserDoesNotExistException,
    UserInactiveException,
)
from app.auth.infrastructure.schemas import TokenSchema
from app.users.infrastructure.repositories.sql_model_user_repository import (
    SqlModelUserRepository,
)

router = APIRouter()


@router.post("/access-token/", response_model=TokenSchema)
def authenticate_user(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> TokenSchema:
    try:
        token = Authenticate(
            repository=SqlModelUserRepository(session=session)
        ).execute(email=form_data.username, password=form_data.password)

    except (UserDoesNotExistException, IncorrectPasswordException):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    except UserInactiveException:
        raise HTTPException(status_code=400, detail="Inactive user")

    return TokenSchema.from_domain(token)
