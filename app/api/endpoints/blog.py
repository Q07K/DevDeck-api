from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.schemas.database_schemas import (
    User, UserCreate, Post, PostCreate, PostUpdate, PostSummary,
    Comment, CommentCreate, Tag, ResponseModel, PaginatedResponse
)
from app.services.database_service import (
    UserService, PostService, CommentService, PostLikeService, TagService
)

router = APIRouter(prefix="/blog", tags=["Blog"])

# 현재 사용자 ID를 가져오는 임시 함수 (실제로는 JWT 토큰에서 추출)
def get_current_user_id() -> int:
    """현재 사용자 ID 반환 (임시 - JWT 구현 후 변경 필요)"""
    return 1  # 테스트용 고정값


# 사용자 관련 엔드포인트
@router.post("/users", response_model=ResponseModel, status_code=201)
async def create_user(user_data: UserCreate):
    """사용자 생성"""
    try:
        user = UserService.create_user(user_data)
        return ResponseModel(
            success=True,
            message="사용자가 성공적으로 생성되었습니다.",
            data=user
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"사용자 생성 실패: {str(e)}")


@router.get("/users/{user_id}", response_model=ResponseModel)
async def get_user(user_id: int):
    """사용자 조회"""
    user = UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    return ResponseModel(
        success=True,
        message="사용자 정보를 성공적으로 조회했습니다.",
        data=user
    )


# 게시글 관련 엔드포인트
@router.post("/posts", response_model=ResponseModel, status_code=201)
async def create_post(
    post_data: PostCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """게시글 생성"""
    try:
        post = PostService.create_post(current_user_id, post_data)
        return ResponseModel(
            success=True,
            message="게시글이 성공적으로 생성되었습니다.",
            data=post
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"게시글 생성 실패: {str(e)}")


@router.get("/posts", response_model=PaginatedResponse)
async def get_posts_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    tag: Optional[str] = Query(None, description="태그 필터")
):
    """게시글 목록 조회 (페이징)"""
    try:
        result = PostService.get_posts_list(page=page, per_page=per_page, tag_name=tag)
        return PaginatedResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"게시글 목록 조회 실패: {str(e)}")


@router.get("/posts/{post_id}", response_model=ResponseModel)
async def get_post(post_id: int):
    """게시글 상세 조회 (조회수 증가)"""
    post = PostService.get_post_by_id(post_id, increment_view=True)
    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    return ResponseModel(
        success=True,
        message="게시글을 성공적으로 조회했습니다.",
        data=post
    )


@router.put("/posts/{post_id}", response_model=ResponseModel)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    """게시글 수정"""
    post = PostService.update_post(post_id, current_user_id, post_data)
    if not post:
        raise HTTPException(
            status_code=404, 
            detail="게시글을 찾을 수 없거나 수정 권한이 없습니다."
        )
    
    return ResponseModel(
        success=True,
        message="게시글이 성공적으로 수정되었습니다.",
        data=post
    )


@router.delete("/posts/{post_id}", response_model=ResponseModel)
async def delete_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """게시글 삭제 (소프트 삭제)"""
    success = PostService.delete_post(post_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없거나 삭제 권한이 없습니다."
        )
    
    return ResponseModel(
        success=True,
        message="게시글이 성공적으로 삭제되었습니다."
    )


# 댓글 관련 엔드포인트
@router.post("/comments", response_model=ResponseModel, status_code=201)
async def create_comment(
    comment_data: CommentCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """댓글 생성"""
    try:
        comment = CommentService.create_comment(current_user_id, comment_data)
        return ResponseModel(
            success=True,
            message="댓글이 성공적으로 생성되었습니다.",
            data=comment
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"댓글 생성 실패: {str(e)}")


@router.get("/posts/{post_id}/comments", response_model=ResponseModel)
async def get_comments_by_post(post_id: int):
    """게시글의 댓글 조회 (계층구조)"""
    try:
        comments = CommentService.get_comments_by_post_id(post_id)
        return ResponseModel(
            success=True,
            message="댓글을 성공적으로 조회했습니다.",
            data={"comments": comments}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"댓글 조회 실패: {str(e)}")


# 좋아요 관련 엔드포인트
@router.post("/posts/{post_id}/like", response_model=ResponseModel)
async def toggle_post_like(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """게시글 좋아요 토글"""
    try:
        result = PostLikeService.toggle_like(current_user_id, post_id)
        return ResponseModel(
            success=True,
            message=f"게시글을 {'좋아요' if result['action'] == 'liked' else '좋아요 취소'}했습니다.",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"좋아요 처리 실패: {str(e)}")


# 태그 관련 엔드포인트
@router.get("/tags", response_model=ResponseModel)
async def get_all_tags():
    """모든 태그 조회 (게시글 수 포함)"""
    try:
        tags = TagService.get_all_tags()
        return ResponseModel(
            success=True,
            message="태그를 성공적으로 조회했습니다.",
            data={"tags": tags}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"태그 조회 실패: {str(e)}")
