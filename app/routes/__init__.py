from fastapi import APIRouter

from app.routes import auth, node

from . import user

api_router = APIRouter()

api_router.include_router(user.router, prefix="/api")
api_router.include_router(auth.router, prefix="/api")
api_router.include_router(node.router, prefix="/api")

__all__ = ["api_router"]