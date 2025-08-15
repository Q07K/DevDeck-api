from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserSignupRequest(BaseModel):
    """회원가입 요청 스키마"""

    email: EmailStr
    password: str
    nickname: str


class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""

    id: int
    email: str
    nickname: str
    createdAt: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    """사용자 정보 수정 요청 스키마"""

    nickname: str | None = None
    password: str | None = None


class UserPublicResponse(BaseModel):
    """공개 사용자 정보 응답 스키마 (다른 사용자 조회용)"""

    id: int
    nickname: str
    createdAt: datetime

    class Config:
        from_attributes = True
