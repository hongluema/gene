from fastapi import APIRouter

from .users import router as users_router
from .wx import router as wx_router
from .projects import router as projects_router
from .organization import router as organization_router
from .sample import router as sample_router


api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(wx_router, prefix="/wx", tags=["wx"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(organization_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(sample_router, prefix="/samples", tags=["samples"])
