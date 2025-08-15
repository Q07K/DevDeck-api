from fastapi import APIRouter

from app.api.endpoints import items, blog, auth

api_router = APIRouter()

# 엔드포인트 라우터들을 포함
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(blog.router)
