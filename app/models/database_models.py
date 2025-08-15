from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    nickname = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    post_likes = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")


class Post(Base):
    """게시글 테이블"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    view_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)  # 소프트 삭제
    
    # 관계 설정
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    post_tags = relationship("PostTag", back_populates="post", cascade="all, delete-orphan")
    post_likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    
    # 인덱스
    __table_args__ = (
        Index('idx_posts_user_id', 'user_id'),
        Index('idx_posts_created_at', 'created_at'),
        Index('idx_posts_deleted_at', 'deleted_at'),
    )


class Tag(Base):
    """태그 테이블"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    
    # 관계 설정
    post_tags = relationship("PostTag", back_populates="tag", cascade="all, delete-orphan")


class Comment(Base):
    """댓글 테이블"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # 대댓글
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    
    # 인덱스
    __table_args__ = (
        Index('idx_comments_post_id', 'post_id'),
        Index('idx_comments_user_id', 'user_id'),
        Index('idx_comments_parent_id', 'parent_comment_id'),
    )


class PostTag(Base):
    """게시글-태그 연결 테이블 (다대다 관계)"""
    __tablename__ = "post_tags"
    
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)
    
    # 관계 설정
    post = relationship("Post", back_populates="post_tags")
    tag = relationship("Tag", back_populates="post_tags")


class PostLike(Base):
    """게시글 좋아요 테이블 (다대다 관계)"""
    __tablename__ = "post_likes"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    
    # 관계 설정
    user = relationship("User", back_populates="post_likes")
    post = relationship("Post", back_populates="post_likes")
