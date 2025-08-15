"""
테스트용 더미 사용자 생성 스크립트
"""

import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import init_database, sqlalchemy_manager
from app.crud.users import create_user, get_user_by_email


def create_test_user():
    """테스트용 사용자 생성"""
    init_database()  # 데이터베이스 초기화

    db = sqlalchemy_manager.get_session()
    try:
        # 이미 존재하는지 확인
        existing_user = get_user_by_email(db, "user@example.com")
        if existing_user:
            print("테스트 사용자가 이미 존재합니다.")
            return

        # 새 사용자 생성
        user = create_user(
            db=db,
            email="user@example.com",
            password="password123",
            nickname="testuser",
        )
        print(f"테스트 사용자 생성됨: {user.email} (ID: {user.id})")

    except Exception as e:
        print(f"사용자 생성 중 오류: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()
