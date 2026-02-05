from fastapi import APIRouter

from .users import router as users_router
from .organization import router as organization_router
from .sample import router as sample_router
from .remote import router as remote_router
from .ocr import router as ocr_router
from .apply import router as apply_router
from .wx import router as wx_router


api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
# api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(organization_router, prefix="/organizations", tags=["organizations"])
api_router.include_router(sample_router, prefix="/samples", tags=["samples"])
api_router.include_router(apply_router, prefix="/applies", tags=["applies"])
api_router.include_router(remote_router, tags=["remote"])  # exposes /api/token
api_router.include_router(ocr_router, prefix="/ocr", tags=["ocr"])
api_router.include_router(wx_router, prefix="/wx", tags=["wx"])
