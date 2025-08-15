from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.users import User


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    이메일로 사용자 조회
    """
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)


def get_user_by_nickname(db: Session, nickname: str) -> User | None:
    """
    닉네임으로 사용자 조회
    """
    stmt = select(User).where(User.nickname == nickname)
    return db.scalar(stmt)


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    ID로 사용자 조회
    """
    stmt = select(User).where(User.id == user_id)
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
    db_user = User(email=email, password=hashed_password, nickname=nickname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session, user: User, nickname: str = None, password: str = None
) -> User:
    """
    사용자 정보 수정
    """
    if nickname is not None:
        user.nickname = nickname
    if password is not None:
        user.password = get_password_hash(password)

    db.commit()
    db.refresh(user)
    return user
