from fastapi import APIRouter
from app.apis.v1.login import router as login_router
from app.apis.v1.user import router as user_router 
from app.apis.v1.register import router as register_router
from app.apis.v1.verification import router as verification_router
from app.apis.v1.health import router as health_router
from app.apis.v1.information import router as information_router
from app.apis.v1.role import router as role_router


router = APIRouter(prefix="/api/v1")
router.include_router(information_router)
router.include_router(login_router)
router.include_router(user_router)
router.include_router(register_router)
router.include_router(verification_router)
router.include_router(health_router)
router.include_router(role_router)
