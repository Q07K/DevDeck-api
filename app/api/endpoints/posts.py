from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.endpoints.auth import get_current_user
from app.models.users import User
from app.crud.posts import (
    create_post, get_post_by_id, get_posts, update_post, delete_post,
    toggle_post_like, get_comment_count, create_comment, get_comment_by_id,
    update_comment, delete_comment
)
from app.schemas.posts import (
    PostCreateRequest, PostUpdateRequest, PostDetailResponse, PostListResponse,
    PostSummaryResponse, LikeResponse, CommentCreateRequest, CommentResponse,
    CommentUpdateRequest, AuthorResponse
)

router = APIRouter(tags=["posts"])


def _create_post_summary_response(post, comment_count: int = None) -> PostSummaryResponse:
    """글 요약 응답 생성 헬퍼 함수"""
    if comment_count is None:
        # 댓글 수는 이미 로드된 관계에서 계산하거나 별도로 조회
        comment_count = len(post.comments) if hasattr(post, 'comments') and post.comments else 0
    
    # 요약 생성 (본문의 첫 100자)
    summary = post.content[:100] + "..." if len(post.content) > 100 else post.content
    
    return PostSummaryResponse(
        id=post.id,
        title=post.title,
        summary=summary,
        likeCount=post.like_count,
        commentCount=comment_count,
        author=AuthorResponse(id=post.author.id, nickname=post.author.nickname),
        createdAt=post.created_at
    )


def _create_comment_response(comment) -> CommentResponse:
    """댓글 응답 생성 헬퍼 함수"""
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        author=AuthorResponse(id=comment.author.id, nickname=comment.author.nickname),
        createdAt=comment.created_at,
        parentCommentId=comment.parent_comment_id,
        replies=[]  # 대댓글은 별도 처리 필요
    )


@router.post("/posts", response_model=PostDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_post_endpoint(
    post_data: PostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """글 작성"""
    try:
        post = create_post(
            db=db,
            title=post_data.title,
            content=post_data.content,
            user_id=current_user.id,
            tags=post_data.tags
        )
        
        # 생성된 글 상세 정보 조회
        created_post = get_post_by_id(db, post.id)
        
        # 태그 정보 추출
        tags = [pt.tag.name for pt in created_post.post_tags] if created_post.post_tags else []
        
        return PostDetailResponse(
            id=created_post.id,
            title=created_post.title,
            content=created_post.content,
            viewCount=created_post.view_count,
            likeCount=created_post.like_count,
            createdAt=created_post.created_at,
            author=AuthorResponse(id=created_post.author.id, nickname=created_post.author.nickname),
            tags=tags,
            comments=[]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"글 작성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/posts", response_model=PostListResponse)
async def get_posts_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    sort: str = Query("latest", regex="^(latest|popular)$"),
    query: str = Query(None),
    tag: str = Query(None),
    db: Session = Depends(get_db)
):
    """글 목록 조회"""
    try:
        posts, total_count = get_posts(
            db=db,
            page=page,
            limit=limit,
            sort=sort,
            query=query,
            tag=tag
        )
        
        total_pages = (total_count + limit - 1) // limit
        
        post_summaries = []
        for post in posts:
            comment_count = get_comment_count(db, post.id)
            post_summaries.append(_create_post_summary_response(post, comment_count))
        
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


@router.get("/posts/{post_id}", response_model=PostDetailResponse)
async def get_post_detail(
    post_id: int,
    db: Session = Depends(get_db)
):
    """글 상세 조회 (조회수 증가)"""
    post = get_post_by_id(db, post_id, increment_view=True)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="글을 찾을 수 없습니다."
        )
    
    # 태그 정보 추출
    tags = [pt.tag.name for pt in post.post_tags] if post.post_tags else []
    
    # 댓글 정보 변환 (대댓글 처리)
    comments = []
    parent_comments = [c for c in post.comments if c.parent_comment_id is None]
    
    for comment in parent_comments:
        comment_response = _create_comment_response(comment)
        # 대댓글 추가
        replies = [c for c in post.comments if c.parent_comment_id == comment.id]
        comment_response.replies = [_create_comment_response(reply) for reply in replies]
        comments.append(comment_response)
    
    return PostDetailResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        viewCount=post.view_count,
        likeCount=post.like_count,
        createdAt=post.created_at,
        author=AuthorResponse(id=post.author.id, nickname=post.author.nickname),
        tags=tags,
        comments=comments
    )


@router.patch("/posts/{post_id}", response_model=PostDetailResponse)
async def update_post_endpoint(
    post_id: int,
    post_data: PostUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """글 수정 (소유권 확인)"""
    post = get_post_by_id(db, post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="글을 찾을 수 없습니다."
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="글 수정 권한이 없습니다."
        )
    
    try:
        updated_post = update_post(
            db=db,
            post=post,
            title=post_data.title,
            content=post_data.content,
            tags=post_data.tags
        )
        
        # 수정된 글 상세 정보 조회
        updated_post = get_post_by_id(db, post_id)
        tags = [pt.tag.name for pt in updated_post.post_tags] if updated_post.post_tags else []
        
        return PostDetailResponse(
            id=updated_post.id,
            title=updated_post.title,
            content=updated_post.content,
            viewCount=updated_post.view_count,
            likeCount=updated_post.like_count,
            createdAt=updated_post.created_at,
            author=AuthorResponse(id=updated_post.author.id, nickname=updated_post.author.nickname),
            tags=tags,
            comments=[]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"글 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_endpoint(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """글 삭제 (소유권 확인)"""
    post = get_post_by_id(db, post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="글을 찾을 수 없습니다."
        )
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="글 삭제 권한이 없습니다."
        )
    
    try:
        delete_post(db=db, post=post, soft_delete=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"글 삭제 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/posts/{post_id}/like", response_model=LikeResponse)
async def toggle_post_like_endpoint(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """글 좋아요/좋아요 취소"""
    post = get_post_by_id(db, post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="글을 찾을 수 없습니다."
        )
    
    try:
        like_count, user_liked = toggle_post_like(db, post_id, current_user.id)
        
        return LikeResponse(
            likeCount=like_count,
            userLiked=user_liked
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"좋아요 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/me/posts", response_model=PostListResponse)
async def get_my_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """내가 쓴 글 목록 조회"""
    try:
        posts, total_count = get_posts(
            db=db,
            page=page,
            limit=limit,
            user_id=current_user.id
        )
        
        total_pages = (total_count + limit - 1) // limit
        
        post_summaries = []
        for post in posts:
            comment_count = get_comment_count(db, post.id)
            post_summaries.append(_create_post_summary_response(post, comment_count))
        
        return PostListResponse(
            posts=post_summaries,
            totalPages=total_pages,
            currentPage=page
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"내 글 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


# 댓글 관련 엔드포인트
@router.post("/posts/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment_endpoint(
    post_id: int,
    comment_data: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """댓글/대댓글 작성"""
    # 글 존재 확인
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="글을 찾을 수 없습니다."
        )
    
    # 부모 댓글 존재 확인 (대댓글인 경우)
    if comment_data.parentCommentId:
        parent_comment = get_comment_by_id(db, comment_data.parentCommentId)
        if not parent_comment or parent_comment.post_id != post_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="부모 댓글을 찾을 수 없습니다."
            )
    
    try:
        comment = create_comment(
            db=db,
            post_id=post_id,
            user_id=current_user.id,
            content=comment_data.content,
            parent_comment_id=comment_data.parentCommentId
        )
        
        # 생성된 댓글 정보 조회
        created_comment = get_comment_by_id(db, comment.id)
        
        return _create_comment_response(created_comment)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 작성 중 오류가 발생했습니다: {str(e)}"
        )


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment_endpoint(
    comment_id: int,
    comment_data: CommentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """댓글 수정 (소유권 확인)"""
    comment = get_comment_by_id(db, comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다."
        )
    
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글 수정 권한이 없습니다."
        )
    
    try:
        updated_comment = update_comment(db=db, comment=comment, content=comment_data.content)
        return _create_comment_response(updated_comment)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_endpoint(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """댓글 삭제 (소유권 확인)"""
    comment = get_comment_by_id(db, comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="댓글을 찾을 수 없습니다."
        )
    
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글 삭제 권한이 없습니다."
        )
    
    try:
        delete_comment(db=db, comment=comment)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 삭제 중 오류가 발생했습니다: {str(e)}"
        )
