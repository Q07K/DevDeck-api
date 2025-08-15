from fastapi import APIRouter

from app.api.endpoints import items

api_router = APIRouter()

# 엔드포인트 라우터들을 포함
api_router.include_router(items.router, prefix="/items", tags=["items"])
