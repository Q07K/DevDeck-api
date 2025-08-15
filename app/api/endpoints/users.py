from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.core.database import get_db
from app.crud.users import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_nickname,
    update_user,
)
from app.models.posts import Post
from app.models.users import User
from app.schemas.users import (
    UserPublicResponse,
    UserResponse,
    UserSignupRequest,
    UserUpdateRequest,
)

router = APIRouter(tags=["users"])


@router.post("/users/signup", response_model=UserResponse, status_code=201)
async def signup(
    signup_data: UserSignupRequest, db: Session = Depends(get_db)
):
    """
    회원가입 - 새로운 사용자 계정을 생성합니다.
    """
    # 이메일 중복 체크
    existing_email = get_user_by_email(db, signup_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용중인 이메일입니다.",
        )

    # 닉네임 중복 체크
    existing_nickname = get_user_by_nickname(db, signup_data.nickname)
    if existing_nickname:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용중인 닉네임입니다.",
        )

    # 사용자 생성
    try:
        user = create_user(
            db=db,
            email=signup_data.email,
            password=signup_data.password,
            nickname=signup_data.nickname,
        )

        return UserResponse(
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            createdAt=user.created_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="회원가입 처리 중 오류가 발생했습니다.",
        )


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    내 정보 조회 - 현재 로그인된 사용자의 정보를 조회합니다.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        nickname=current_user.nickname,
        createdAt=current_user.created_at,
    )


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    내 정보 수정 - 현재 로그인된 사용자의 정보를 수정합니다.
    """
    # 닉네임 변경 시 중복 체크
    if update_data.nickname and update_data.nickname != current_user.nickname:
        existing_nickname = get_user_by_nickname(db, update_data.nickname)
        if existing_nickname:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 사용중인 닉네임입니다.",
            )

    try:
        updated_user = update_user(
            db=db,
            user=current_user,
            nickname=update_data.nickname,
            password=update_data.password,
        )

        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            nickname=updated_user.nickname,
            createdAt=updated_user.created_at,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="정보 수정 중 오류가 발생했습니다.",
        )


@router.get("/users/{user_id}", response_model=UserPublicResponse)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """
    특정 사용자 정보 조회 - 공개 정보만 반환합니다.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    return UserPublicResponse(
        id=user.id, nickname=user.nickname, createdAt=user.created_at
    )


@router.get("/users/{user_id}/posts")
async def get_user_posts(
    user_id: int,
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 글 개수"),
    db: Session = Depends(get_db),
):
    """
    특정 사용자가 작성한 글 목록 조회
    """
    # 사용자 존재 확인
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    # 페이지네이션 계산
    offset = (page - 1) * limit

    try:
        # 해당 사용자의 글 조회
        stmt = (
            select(Post)
            .where(Post.user_id == user_id)
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        posts = db.scalars(stmt).all()

        # 전체 글 개수 조회
        total_stmt = select(Post).where(Post.user_id == user_id)
        total_count = len(db.scalars(total_stmt).all())

        # 응답 데이터 구성
        post_list = []
        for post in posts:
            post_data = {
                "id": post.id,
                "title": post.title,
                "content": (
                    post.content[:200] + "..."
                    if len(post.content) > 200
                    else post.content
                ),
                "author": {
                    "id": post.author.id,
                    "nickname": post.author.nickname,
                },
                "createdAt": post.created_at,
                "updatedAt": post.updated_at,
            }
            post_list.append(post_data)

        return {
            "posts": post_list,
            "pagination": {
                "currentPage": page,
                "totalPages": (total_count + limit - 1) // limit,
                "totalCount": total_count,
                "hasNext": page * limit < total_count,
                "hasPrevious": page > 1,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="글 목록 조회 중 오류가 발생했습니다.",
        )
