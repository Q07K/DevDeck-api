from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.endpoints.auth import get_current_user
from app.models.users import User
from app.crud.posts import (
    get_dashboard_stats, get_posts, get_post_by_id, delete_post,
    get_comment_by_id, delete_comment
)
from app.schemas.posts import (
    AdminDashboardResponse, AdminDeleteRequest, PostListResponse,
    PostSummaryResponse, AnnouncementCreateRequest, AnnouncementResponse
)

router = APIRouter(prefix="/admin", tags=["admin"])


def check_admin_permission(current_user: User):
    """관리자 권한 확인 (임시 구현 - 실제로는 role 기반으로 구현)"""
    # 임시로 특정 사용자를 관리자로 간주
    if current_user.email not in ["admin@example.com", "user@example.com"]:  # 테스트용
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다."
        )


@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """관리자 대시보드 통계 조회"""
    check_admin_permission(current_user)
    
    try:
        stats = get_dashboard_stats(db)
        return AdminDashboardResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대시보드 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/posts", response_model=PostListResponse)
async def get_admin_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """관리자용 전체 글 목록 조회"""
    check_admin_permission(current_user)
    
    try:
        posts, total_count = get_posts(db=db, page=page, limit=limit)
        total_pages = (total_count + limit - 1) // limit
        
        post_summaries = []
        for post in posts:
            # 글 요약 생성
            summary = post.content[:100] + "..." if len(post.content) > 100 else post.content
            post_summaries.append(PostSummaryResponse(
                id=post.id,
                title=post.title,
                summary=summary,
                likeCount=post.like_count,
                commentCount=len(post.comments) if post.comments else 0,
                author={"id": post.author.id, "nickname": post.author.nickname},
                createdAt=post.created_at
            ))
        
        return PostListResponse(
            posts=post_summaries,
            totalPages=total_pages,
            currentPage=page
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"글 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_post(
    post_id: int,
    delete_request: AdminDeleteRequest = AdminDeleteRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """관리자에 의한 글 삭제"""
    check_admin_permission(current_user)
    
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="글을 찾을 수 없습니다."
        )
    
    try:
        soft_delete = delete_request.deleteType == "soft"
        delete_post(db=db, post=post, soft_delete=soft_delete)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"글 삭제 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """관리자에 의한 댓글 삭제"""
    check_admin_permission(current_user)
    
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다."
        )
    
    try:
        delete_comment(db=db, comment=comment)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 삭제 중 오류가 발생했습니다: {str(e)}"
        )


# 공지사항 관련 (간단한 구현)
announcements_storage = []  # 임시 저장소 (실제로는 DB 모델 필요)


@router.post("/announcements", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement_data: AnnouncementCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """공지사항 작성"""
    check_admin_permission(current_user)
    
    from datetime import datetime
    
    announcement = {
        "id": len(announcements_storage) + 1,
        "title": announcement_data.title,
        "content": announcement_data.content,
        "isActive": announcement_data.isActive,
        "createdAt": datetime.utcnow()
    }
    
    announcements_storage.append(announcement)
    
    return AnnouncementResponse(**announcement)


@router.get("/announcements", response_model=list[AnnouncementResponse])
async def get_active_announcements():
    """활성화된 공지사항 조회 (일반 사용자용)"""
    active_announcements = [
        ann for ann in announcements_storage if ann["isActive"]
    ]
    
    return [AnnouncementResponse(**ann) for ann in active_announcements]
