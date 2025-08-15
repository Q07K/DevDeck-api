from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class AuthorResponse(BaseModel):
    """작성자 정보 응답 스키마"""
    id: int
    nickname: str
    
    class Config:
        from_attributes = True


class PostCreateRequest(BaseModel):
    """글 작성 요청 스키마"""
    title: str
    content: str
    tags: List[str] = []


class PostUpdateRequest(BaseModel):
    """글 수정 요청 스키마"""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class PostSummaryResponse(BaseModel):
    """글 목록용 요약 응답 스키마"""
    id: int
    title: str
    summary: str
    likeCount: int
    commentCount: int
    author: AuthorResponse
    createdAt: datetime
    
    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """댓글 응답 스키마"""
    id: int
    content: str
    author: AuthorResponse
    createdAt: datetime
    parentCommentId: Optional[int] = None
    replies: List["CommentResponse"] = []
    
    class Config:
        from_attributes = True


class PostDetailResponse(BaseModel):
    """글 상세 응답 스키마"""
    id: int
    title: str
    content: str
    viewCount: int
    likeCount: int
    createdAt: datetime
    author: AuthorResponse
    tags: List[str] = []
    comments: List[CommentResponse] = []
    
    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """글 목록 응답 스키마"""
    posts: List[PostSummaryResponse]
    totalPages: int
    currentPage: int
    
    class Config:
        from_attributes = True


class LikeResponse(BaseModel):
    """좋아요 응답 스키마"""
    likeCount: int
    userLiked: bool


class CommentCreateRequest(BaseModel):
    """댓글 작성 요청 스키마"""
    content: str
    parentCommentId: Optional[int] = None


class CommentUpdateRequest(BaseModel):
    """댓글 수정 요청 스키마"""
    content: str


class PaginationResponse(BaseModel):
    """페이지네이션 응답 스키마"""
    currentPage: int
    totalPages: int
    totalCount: int
    hasNext: bool
    hasPrevious: bool


# Admin 관련 스키마
class AdminDashboardResponse(BaseModel):
    """관리자 대시보드 응답 스키마"""
    totalUsers: int
    todaySignups: int
    totalPosts: int
    todayPosts: int
    totalComments: int


class AdminDeleteRequest(BaseModel):
    """관리자 삭제 요청 스키마"""
    deleteType: str = "soft"  # 'soft' or 'hard'


class AnnouncementCreateRequest(BaseModel):
    """공지사항 작성 요청 스키마"""
    title: str
    content: str
    isActive: bool = True


class AnnouncementResponse(BaseModel):
    """공지사항 응답 스키마"""
    id: int
    title: str
    content: str
    isActive: bool
    createdAt: datetime
    
    class Config:
        from_attributes = True
