from fastapi import APIRouter

from app.api.endpoints import admin, auth, posts, users

api_router = APIRouter()

# 엔드포인트 라우터들을 포함
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(posts.router, tags=["posts"])
api_router.include_router(admin.router, tags=["admin"])

# 공지사항은 별도 경로로 추가 (일반 사용자용)
api_router.include_router(
    admin.router, prefix="/announcements", tags=["announcements"]
)
