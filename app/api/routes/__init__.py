from fastapi import APIRouter

from .math import router as math_router
from .users import router as users_router


api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(math_router, prefix="/math", tags=["math"])

