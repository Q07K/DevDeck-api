from app.models.database_models import Base


from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship


class PostTag(Base):
    """게시글-태그 연결 테이블 (다대다 관계)"""
    __tablename__ = "post_tags"

    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

    # 관계 설정
    post = relationship("Post", back_populates="post_tags")
    tag = relationship("Tag", back_populates="post_tags")