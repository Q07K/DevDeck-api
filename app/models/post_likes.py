from app.models.database_models import Base


from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class PostLike(Base):
    """게시글 좋아요 테이블 (다대다 관계)"""
    __tablename__ = "post_likes"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)

    # 관계 설정
    user = relationship("User", back_populates="post_likes")
    post = relationship("Post", back_populates="post_likes")