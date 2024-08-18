from fastapi import APIRouter

from app.auth.infrastructure.api import endpoints as auth_endpoints
from app.users.infrastructure.api import endpoints as user_endpoints

api_router = APIRouter()
api_router.include_router(auth_endpoints.router, prefix="/auth", tags=["auth"])
api_router.include_router(user_endpoints.router, prefix="/users", tags=["users"])
