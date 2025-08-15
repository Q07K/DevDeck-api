from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Sequence,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database_models import Base


class Comment(Base):
    """댓글 테이블"""

    __tablename__ = "comments"

    id = Column(Integer, Sequence("comments_id_seq"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_comment_id = Column(
        Integer, ForeignKey("comments.id"), nullable=True
    )  # 대댓글
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # 관계 설정
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

    # 인덱스
    __table_args__ = (
        Index("idx_comments_post_id", "post_id"),
        Index("idx_comments_user_id", "user_id"),
        Index("idx_comments_parent_id", "parent_comment_id"),
    )
