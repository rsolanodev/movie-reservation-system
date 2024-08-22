from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.users.actions.create_user import CreateUser, CreateUserParams
from app.users.domain.exceptions import UserAlreadyExistsException
from app.users.infrastructure.api.schemas import CreateUserSchema, UserSchema
from app.users.infrastructure.repositories.sql_model_user_repository import (
    SqlModelUserRepository,
)

router = APIRouter()


@router.post(
    "/",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    session: SessionDep, create_user_schema: CreateUserSchema
) -> UserSchema:
    try:
        user = CreateUser(
            repository=SqlModelUserRepository(session=session),
        ).execute(
            params=CreateUserParams(
                email=create_user_schema.email,
                password=create_user_schema.password,
                full_name=create_user_schema.full_name,
            )
        )
    except UserAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists",
        )
    return UserSchema.from_domain(user)
