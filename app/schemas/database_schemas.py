from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User 스키마
class UserBase(BaseModel):
    email: EmailStr
    nickname: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Tag 스키마
class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    
    class Config:
        from_attributes = True


# Post 스키마
class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    tag_names: Optional[List[str]] = []


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tag_names: Optional[List[str]] = None


class Post(PostBase):
    id: int
    user_id: int
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    author: User
    tags: List[Tag] = []
    
    class Config:
        from_attributes = True


class PostSummary(BaseModel):
    """게시글 목록용 간단한 정보"""
    id: int
    title: str
    user_id: int
    author_nickname: str
    view_count: int
    like_count: int
    created_at: datetime
    tags: List[str] = []
    
    class Config:
        from_attributes = True


# Comment 스키마
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    post_id: int
    parent_comment_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: str


class Comment(CommentBase):
    id: int
    post_id: int
    user_id: int
    parent_comment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    author: User
    replies: List['Comment'] = []
    
    class Config:
        from_attributes = True


# PostLike 스키마
class PostLikeCreate(BaseModel):
    post_id: int


class PostLike(BaseModel):
    user_id: int
    post_id: int
    
    class Config:
        from_attributes = True


# Response 스키마
class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    per_page: int
    total_pages: int
