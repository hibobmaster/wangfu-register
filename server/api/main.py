from fastapi import APIRouter

from api.routes import captcha, verify, user

api_router = APIRouter()
api_router.include_router(captcha.router, prefix="/captcha", tags=["captcha"])
api_router.include_router(verify.router, prefix="/verify", tags=["verify"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
