"""
데이터베이스 사용자 확인 및 생성 스크립트
"""

import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.core.database import init_database, sqlalchemy_manager
from app.crud.users import create_user, get_user_by_email
from app.models.users import User


def list_all_users():
    """모든 사용자 목록 조회"""
    print("=== 데이터베이스 사용자 목록 ===")

    db = sqlalchemy_manager.get_session()
    try:
        stmt = select(User)
        users = db.scalars(stmt).all()

        if not users:
            print("데이터베이스에 사용자가 없습니다.")
        else:
            for user in users:
                print(
                    f"ID: {user.id}, Email: {user.email}, Nickname: {user.nickname}"
                )

    except Exception as e:
        print(f"사용자 목록 조회 중 오류: {e}")
    finally:
        db.close()


def create_test_users():
    """테스트용 사용자들 생성"""
    print("\n=== 테스트 사용자 생성 ===")

    db = sqlalchemy_manager.get_session()
    try:
        test_users = [
            {
                "email": "user@example.com",
                "password": "password123",
                "nickname": "testuser1",
            },
            {
                "email": "admin@example.com",
                "password": "admin123",
                "nickname": "admin",
            },
        ]

        for user_data in test_users:
            existing_user = get_user_by_email(db, user_data["email"])
            if existing_user:
                print(f"사용자 {user_data['email']}는 이미 존재합니다.")
                continue

            try:
                user = create_user(
                    db=db,
                    email=user_data["email"],
                    password=user_data["password"],
                    nickname=user_data["nickname"],
                )
                print(f"✓ 사용자 생성됨: {user.email} (ID: {user.id})")
            except Exception as e:
                print(f"❌ 사용자 {user_data['email']} 생성 실패: {e}")
                db.rollback()

    except Exception as e:
        print(f"사용자 생성 중 전체 오류: {e}")
        db.rollback()
    finally:
        db.close()


def verify_user_password():
    """사용자 비밀번호 검증"""
    print("\n=== 사용자 인증 테스트 ===")

    from app.crud.users import authenticate_user

    db = sqlalchemy_manager.get_session()
    try:
        # 테스트 인증
        user = authenticate_user(db, "user@example.com", "password123")
        if user:
            print(f"✓ 인증 성공: {user.email}")
        else:
            print("❌ 인증 실패")

    except Exception as e:
        print(f"인증 테스트 중 오류: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()  # 데이터베이스 초기화

    # 1. 현재 사용자 목록 확인
    list_all_users()

    # 2. 테스트 사용자 생성
    create_test_users()

    # 3. 생성 후 사용자 목록 다시 확인
    list_all_users()

    # 4. 사용자 인증 테스트
    verify_user_password()
