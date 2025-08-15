from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import settings
from app.core.database import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작 시 데이터베이스 초기화
    init_database()
    yield
    # 종료 시 정리 작업 (필요시)


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 팩토리"""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        lifespan=lifespan,
    )

    # CORS 미들웨어 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API 라우터 포함
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "DevDeck API is running!"}


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}
