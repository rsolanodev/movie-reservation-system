from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.users.application.create_user import CreateUser, CreateUserParams
from app.users.domain.exceptions import UserAlreadyExists
from app.users.infrastructure.api.payloads import CreateUserPayload
from app.users.infrastructure.api.responses import UserResponse
from app.users.infrastructure.repositories.sqlmodel_user_repository import (
    SqlModelUserRepository,
)

router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(session: SessionDep, request_body: CreateUserPayload) -> UserResponse:
    try:
        user = CreateUser(
            repository=SqlModelUserRepository(session=session),
        ).execute(
            params=CreateUserParams(
                email=request_body.email,
                password=request_body.password,
                full_name=request_body.full_name,
            )
        )
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists",
        )
    return UserResponse.from_domain(user)
