from sqlalchemy import Column, DateTime, Integer, Sequence, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.database_models import Base


class User(Base):
    """사용자 테이블"""

    __tablename__ = "users"

    id = Column(Integer, Sequence("users_id_seq"), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50), unique=True, nullable=False, index=True)
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

    # 관계 설정
    posts = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )
    comments = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )
    post_likes = relationship(
        "PostLike", back_populates="user", cascade="all, delete-orphan"
    )
