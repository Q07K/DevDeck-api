from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, desc, and_, or_
from datetime import datetime, date

from app.models.posts import Post
from app.models.comments import Comment
from app.models.users import User
from app.models.post_likes import PostLike
from app.models.tags import Tag
from app.models.post_tags import PostTag


def create_post(db: Session, title: str, content: str, user_id: int, tags: List[str] = None) -> Post:
    """새 글 생성"""
    db_post = Post(
        title=title,
        content=content,
        user_id=user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # 태그 처리
    if tags:
        for tag_name in tags:
            # 태그가 존재하지 않으면 생성
            tag = db.scalar(select(Tag).where(Tag.name == tag_name))
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            
            # 글과 태그 연결
            post_tag = PostTag(post_id=db_post.id, tag_id=tag.id)
            db.add(post_tag)
    
    db.commit()
    return db_post


def get_post_by_id(db: Session, post_id: int, increment_view: bool = False) -> Post | None:
    """ID로 글 조회"""
    stmt = select(Post).options(
        joinedload(Post.author),
        joinedload(Post.comments).joinedload(Comment.author),
        joinedload(Post.post_tags).joinedload(PostTag.tag)
    ).where(and_(Post.id == post_id, Post.deleted_at.is_(None)))
    
    post = db.scalars(stmt).unique().first()
    
    if post and increment_view:
        post.view_count += 1
        db.commit()
        db.refresh(post)
    
    return post


def get_posts(
    db: Session,
    page: int = 1,
    limit: int = 10,
    sort: str = "latest",
    query: str = None,
    tag: str = None,
    user_id: int = None
) -> tuple[List[Post], int]:
    """글 목록 조회 (페이징, 검색, 필터링)"""
    
    stmt = select(Post).options(
        joinedload(Post.author),
        joinedload(Post.post_tags).joinedload(PostTag.tag)
    ).where(Post.deleted_at.is_(None))
    
    # 검색어 필터
    if query:
        stmt = stmt.where(
            or_(
                Post.title.ilike(f"%{query}%"),
                Post.content.ilike(f"%{query}%")
            )
        )
    
    # 태그 필터
    if tag:
        stmt = stmt.join(PostTag).join(Tag).where(Tag.name == tag)
    
    # 사용자 필터
    if user_id:
        stmt = stmt.where(Post.user_id == user_id)
    
    # 정렬
    if sort == "popular":
        stmt = stmt.order_by(desc(Post.like_count))
    else:  # latest
        stmt = stmt.order_by(desc(Post.created_at))
    
    # 총 개수 계산
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = db.scalar(count_stmt)
    
    # 페이징
    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)
    
    posts = db.scalars(stmt).unique().all()
    
    return posts, total_count


def update_post(db: Session, post: Post, title: str = None, content: str = None, tags: List[str] = None) -> Post:
    """글 수정"""
    if title is not None:
        post.title = title
    if content is not None:
        post.content = content
    
    # 태그 업데이트
    if tags is not None:
        # 기존 태그 연결 삭제
        db.query(PostTag).filter(PostTag.post_id == post.id).delete()
        
        # 새 태그 연결
        for tag_name in tags:
            tag = db.scalar(select(Tag).where(Tag.name == tag_name))
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            
            post_tag = PostTag(post_id=post.id, tag_id=tag.id)
            db.add(post_tag)
    
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post: Post, soft_delete: bool = True):
    """글 삭제 (소프트/하드 삭제)"""
    if soft_delete:
        post.deleted_at = datetime.utcnow()
        db.commit()
    else:
        db.delete(post)
        db.commit()


def toggle_post_like(db: Session, post_id: int, user_id: int) -> tuple[int, bool]:
    """글 좋아요 토글"""
    # 기존 좋아요 확인
    like = db.scalar(
        select(PostLike).where(
            and_(PostLike.post_id == post_id, PostLike.user_id == user_id)
        )
    )
    
    post = db.scalar(select(Post).where(Post.id == post_id))
    if not post:
        return 0, False
    
    if like:
        # 좋아요 취소
        db.delete(like)
        post.like_count = max(0, post.like_count - 1)
        user_liked = False
    else:
        # 좋아요 추가
        new_like = PostLike(post_id=post_id, user_id=user_id)
        db.add(new_like)
        post.like_count += 1
        user_liked = True
    
    db.commit()
    db.refresh(post)
    
    return post.like_count, user_liked


def get_comment_count(db: Session, post_id: int) -> int:
    """글의 댓글 수 조회"""
    return db.scalar(
        select(func.count(Comment.id)).where(Comment.post_id == post_id)
    ) or 0


def create_comment(db: Session, post_id: int, user_id: int, content: str, parent_comment_id: int = None) -> Comment:
    """댓글 생성"""
    db_comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content,
        parent_comment_id=parent_comment_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comment_by_id(db: Session, comment_id: int) -> Comment | None:
    """ID로 댓글 조회"""
    return db.scalar(
        select(Comment).options(joinedload(Comment.author)).where(Comment.id == comment_id)
    )


def update_comment(db: Session, comment: Comment, content: str) -> Comment:
    """댓글 수정"""
    comment.content = content
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment: Comment):
    """댓글 삭제"""
    db.delete(comment)
    db.commit()


# Admin 관련 함수들
def get_dashboard_stats(db: Session) -> dict:
    """관리자 대시보드 통계"""
    today = date.today()
    
    total_users = db.scalar(select(func.count(User.id))) or 0
    today_signups = db.scalar(
        select(func.count(User.id)).where(func.date(User.created_at) == today)
    ) or 0
    
    total_posts = db.scalar(
        select(func.count(Post.id)).where(Post.deleted_at.is_(None))
    ) or 0
    today_posts = db.scalar(
        select(func.count(Post.id)).where(
            and_(func.date(Post.created_at) == today, Post.deleted_at.is_(None))
        )
    ) or 0
    
    total_comments = db.scalar(select(func.count(Comment.id))) or 0
    
    return {
        "totalUsers": total_users,
        "todaySignups": today_signups,
        "totalPosts": total_posts,
        "todayPosts": today_posts,
        "totalComments": total_comments
    }
