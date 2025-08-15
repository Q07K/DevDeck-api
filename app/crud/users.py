from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.users import User
from app.core.security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    이메일로 사용자 조회
    """
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    사용자 인증
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_user(db: Session, email: str, password: str, nickname: str) -> User:
    """
    새 사용자 생성
    """
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        password=hashed_password,
        nickname=nickname
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
