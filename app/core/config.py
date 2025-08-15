from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 기본 설정
    PROJECT_NAME: str = "DevDeck API"
    PROJECT_DESCRIPTION: str = "DevDeck 프로젝트를 위한 FastAPI 백엔드"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"

    # CORS 설정
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
    ]

    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # 데이터베이스 설정 (DuckDB 사용)
    DATABASE_URL: str = "duckdb:///./test_devdeck.duckdb"
    DUCKDB_FILE: str = "./test_devdeck.duckdb"

    # JWT 설정 (필요시 사용)
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
