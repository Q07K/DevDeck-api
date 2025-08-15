from sqlalchemy import Column, Integer, Sequence, String
from sqlalchemy.orm import relationship

from app.models.database_models import Base


class Tag(Base):
    """태그 테이블"""

    __tablename__ = "tags"

    id = Column(Integer, Sequence("tags_id_seq"), primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    # 관계 설정
    post_tags = relationship(
        "PostTag",
        back_populates="tag",
        cascade="all, delete-orphan",
    )
