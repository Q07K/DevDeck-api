from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Sequence,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database_models import Base


class Post(Base):
    """게시글 테이블"""

    __tablename__ = "posts"

    id = Column(Integer, Sequence("posts_id_seq"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    view_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
    deleted_at = Column(DateTime, nullable=True)  # 소프트 삭제

    # 관계 설정
    author = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
    )
    post_tags = relationship(
        "PostTag",
        back_populates="post",
        cascade="all, delete-orphan",
    )
    post_likes = relationship(
        "PostLike",
        back_populates="post",
        cascade="all, delete-orphan",
    )

    # 인덱스
    __table_args__ = (
        Index("idx_posts_user_id", "user_id"),
        Index("idx_posts_created_at", "created_at"),
        Index("idx_posts_deleted_at", "deleted_at"),
    )
