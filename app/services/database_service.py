import hashlib
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models import Comment, Post, PostLike, PostTag, Tag, User
from app.schemas.database_schemas import (
    CommentCreate,
    CommentUpdate,
    PostCreate,
    PostUpdate,
    TagCreate,
    UserCreate,
    UserUpdate,
)


class UserService:
    """사용자 관련 서비스"""

    @staticmethod
    def hash_password(password: str) -> str:
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """사용자 생성"""
        hashed_password = UserService.hash_password(user_data.password)

        db_user = User(
            email=user_data.email,
            password=hashed_password,
            nickname=user_data.nickname,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_nickname(db: Session, nickname: str) -> Optional[User]:
        """닉네임으로 사용자 조회"""
        return db.query(User).filter(User.nickname == nickname).first()

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """사용자 목록 조회"""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(
        db: Session, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        """사용자 정보 수정"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["password"] = UserService.hash_password(
                update_data["password"]
            )

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = func.now()
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """사용자 삭제"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return UserService.hash_password(plain_password) == hashed_password


class PostService:
    """게시글 관련 서비스"""

    @staticmethod
    def create_post(db: Session, post_data: PostCreate, user_id: int) -> Post:
        """게시글 생성"""
        db_post = Post(
            user_id=user_id, title=post_data.title, content=post_data.content
        )

        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        # 태그 처리
        if post_data.tag_names:
            for tag_name in post_data.tag_names:
                # 태그 존재 확인 또는 생성
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.commit()
                    db.refresh(tag)

                # 게시글-태그 연결
                post_tag = PostTag(post_id=db_post.id, tag_id=tag.id)
                db.add(post_tag)

        db.commit()
        return db_post

    @staticmethod
    def get_post_by_id(db: Session, post_id: int) -> Optional[Post]:
        """ID로 게시글 조회"""
        return (
            db.query(Post)
            .filter(and_(Post.id == post_id, Post.deleted_at.is_(None)))
            .first()
        )

    @staticmethod
    def get_posts(db: Session, skip: int = 0, limit: int = 100) -> List[Post]:
        """게시글 목록 조회 (삭제되지 않은 것만)"""
        return (
            db.query(Post)
            .filter(Post.deleted_at.is_(None))
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_posts_by_user(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        """특정 사용자의 게시글 목록 조회"""
        return (
            db.query(Post)
            .filter(and_(Post.user_id == user_id, Post.deleted_at.is_(None)))
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_post(
        db: Session, post_id: int, post_data: PostUpdate, user_id: int
    ) -> Optional[Post]:
        """게시글 수정"""
        db_post = (
            db.query(Post)
            .filter(
                and_(
                    Post.id == post_id,
                    Post.user_id == user_id,
                    Post.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not db_post:
            return None

        update_data = post_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field != "tag_names":
                setattr(db_post, field, value)

        db_post.updated_at = func.now()

        # 태그 업데이트 처리
        if "tag_names" in update_data:
            # 기존 태그 연결 삭제
            db.query(PostTag).filter(PostTag.post_id == post_id).delete()

            # 새 태그 연결
            for tag_name in update_data["tag_names"]:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.commit()
                    db.refresh(tag)

                post_tag = PostTag(post_id=post_id, tag_id=tag.id)
                db.add(post_tag)

        db.commit()
        db.refresh(db_post)
        return db_post

    @staticmethod
    def delete_post(db: Session, post_id: int, user_id: int) -> bool:
        """게시글 삭제 (소프트 삭제)"""
        db_post = (
            db.query(Post)
            .filter(
                and_(
                    Post.id == post_id,
                    Post.user_id == user_id,
                    Post.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not db_post:
            return False

        db_post.deleted_at = func.now()
        db.commit()
        return True

    @staticmethod
    def increment_view_count(db: Session, post_id: int) -> bool:
        """조회수 증가"""
        db_post = (
            db.query(Post)
            .filter(and_(Post.id == post_id, Post.deleted_at.is_(None)))
            .first()
        )

        if not db_post:
            return False

        db_post.view_count += 1
        db.commit()
        return True


class CommentService:
    """댓글 관련 서비스"""

    @staticmethod
    def create_comment(
        db: Session, comment_data: CommentCreate, user_id: int
    ) -> Comment:
        """댓글 생성"""
        db_comment = Comment(
            post_id=comment_data.post_id,
            user_id=user_id,
            parent_comment_id=comment_data.parent_comment_id,
            content=comment_data.content,
        )

        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def get_comments_by_post(db: Session, post_id: int) -> List[Comment]:
        """게시글의 댓글 목록 조회"""
        return (
            db.query(Comment)
            .filter(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
            .all()
        )

    @staticmethod
    def get_comment_by_id(db: Session, comment_id: int) -> Optional[Comment]:
        """ID로 댓글 조회"""
        return db.query(Comment).filter(Comment.id == comment_id).first()

    @staticmethod
    def update_comment(
        db: Session, comment_id: int, comment_data: CommentUpdate, user_id: int
    ) -> Optional[Comment]:
        """댓글 수정"""
        db_comment = (
            db.query(Comment)
            .filter(and_(Comment.id == comment_id, Comment.user_id == user_id))
            .first()
        )

        if not db_comment:
            return None

        db_comment.content = comment_data.content
        db_comment.updated_at = func.now()

        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def delete_comment(db: Session, comment_id: int, user_id: int) -> bool:
        """댓글 삭제"""
        db_comment = (
            db.query(Comment)
            .filter(and_(Comment.id == comment_id, Comment.user_id == user_id))
            .first()
        )

        if not db_comment:
            return False

        db.delete(db_comment)
        db.commit()
        return True


class TagService:
    """태그 관련 서비스"""

    @staticmethod
    def create_tag(db: Session, tag_data: TagCreate) -> Tag:
        """태그 생성"""
        db_tag = Tag(name=tag_data.name)
        db.add(db_tag)
        db.commit()
        db.refresh(db_tag)
        return db_tag

    @staticmethod
    def get_tags(db: Session, skip: int = 0, limit: int = 100) -> List[Tag]:
        """태그 목록 조회"""
        return db.query(Tag).offset(skip).limit(limit).all()

    @staticmethod
    def get_tag_by_name(db: Session, name: str) -> Optional[Tag]:
        """이름으로 태그 조회"""
        return db.query(Tag).filter(Tag.name == name).first()

    @staticmethod
    def get_popular_tags(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """인기 태그 조회 (사용 횟수 기준)"""
        result = (
            db.query(Tag.name, func.count(PostTag.tag_id).label("usage_count"))
            .join(PostTag)
            .group_by(Tag.id, Tag.name)
            .order_by(func.count(PostTag.tag_id).desc())
            .limit(limit)
            .all()
        )

        return [{"name": name, "usage_count": count} for name, count in result]


class PostLikeService:
    """게시글 좋아요 관련 서비스"""

    @staticmethod
    def toggle_like(db: Session, post_id: int, user_id: int) -> Dict[str, Any]:
        """좋아요 토글 (좋아요/취소)"""
        # 기존 좋아요 확인
        existing_like = (
            db.query(PostLike)
            .filter(
                and_(PostLike.post_id == post_id, PostLike.user_id == user_id)
            )
            .first()
        )

        if existing_like:
            # 좋아요 취소
            db.delete(existing_like)
            # 게시글 좋아요 수 감소
            post = db.query(Post).filter(Post.id == post_id).first()
            if post:
                post.like_count = max(0, post.like_count - 1)
            action = "unliked"
        else:
            # 좋아요 추가
            new_like = PostLike(post_id=post_id, user_id=user_id)
            db.add(new_like)
            # 게시글 좋아요 수 증가
            post = db.query(Post).filter(Post.id == post_id).first()
            if post:
                post.like_count += 1
            action = "liked"

        db.commit()

        # 현재 좋아요 수 반환
        current_count = (
            db.query(Post).filter(Post.id == post_id).first().like_count
        )

        return {"action": action, "like_count": current_count}

    @staticmethod
    def get_user_likes(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        """사용자가 좋아요한 게시글 목록"""
        return (
            db.query(Post)
            .join(PostLike)
            .filter(
                and_(PostLike.user_id == user_id, Post.deleted_at.is_(None))
            )
            .order_by(PostLike.post_id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
