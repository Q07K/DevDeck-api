from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""
    accessToken: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """토큰 데이터 스키마"""
    email: str | None = None
