from fastapi import APIRouter

from .users import router as users_router
from .wx import router as wx_router


api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(wx_router, prefix="/wx", tags=["wx"])
