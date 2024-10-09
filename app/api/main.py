from fastapi import APIRouter

from app.auth.infrastructure.api import endpoints as auth_endpoints
from app.movies.infrastructure.api import endpoints as movie_endpoints
from app.rooms.infrastructure.api import endpoints as rooms_endpoints
from app.showtimes.infrastructure.api import endpoints as showtimes_endpoints
from app.users.infrastructure.api import endpoints as user_endpoints

api_router = APIRouter()
api_router.include_router(auth_endpoints.router, prefix="/auth", tags=["auth"])
api_router.include_router(user_endpoints.router, prefix="/users", tags=["users"])
api_router.include_router(movie_endpoints.router, prefix="/movies", tags=["movies"])
api_router.include_router(showtimes_endpoints.router, prefix="/showtimes", tags=["showtimes"])
api_router.include_router(rooms_endpoints.router, prefix="/rooms", tags=["rooms"])
