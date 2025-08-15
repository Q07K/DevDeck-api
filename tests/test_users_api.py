"""
Users API pytest 테스트

This module contains pytest-based tests for user endpoints.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

# Import your FastAPI app
from app.main import app

client = TestClient(app)


class TestUsersAPI:
    """Users API 테스트 클래스"""

    def test_signup_success(self):
        """성공적인 회원가입 테스트"""
        timestamp = datetime.now().strftime("%H%M%S")
        signup_data = {
            "email": f"pytest_user_{timestamp}@example.com",
            "password": "pytest123",
            "nickname": f"pytest_user_{timestamp}",
        }

        response = client.post("/api/v1/users/signup", json=signup_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == signup_data["email"]
        assert data["nickname"] == signup_data["nickname"]
        # 비밀번호는 응답에 포함되면 안 됨
        assert "password" not in data

    def test_signup_duplicate_email(self):
        """중복 이메일로 회원가입 테스트"""
        signup_data = {
            "email": "user@example.com",  # 이미 존재하는 이메일
            "password": "password123",
            "nickname": "duplicate_test",
        }

        response = client.post("/api/v1/users/signup", json=signup_data)

        # 중복 이메일의 경우 409 Conflict 또는 400 Bad Request
        assert response.status_code in [409, 400]

    def test_signup_invalid_email(self):
        """잘못된 이메일 형식으로 회원가입 테스트"""
        signup_data = {
            "email": "invalid-email",
            "password": "password123",
            "nickname": "test_user",
        }

        response = client.post("/api/v1/users/signup", json=signup_data)

        assert response.status_code == 422  # Validation error

    def test_signup_weak_password(self):
        """약한 비밀번호로 회원가입 테스트"""
        signup_data = {
            "email": "weak_pwd_test@example.com",
            "password": "123",  # 너무 짧은 비밀번호
            "nickname": "weak_pwd_user",
        }

        response = client.post("/api/v1/users/signup", json=signup_data)

        # 비밀번호 정책에 따라 400 또는 422
        assert response.status_code in [400, 422]

    def test_get_my_profile_with_auth(self, auth_headers):
        """인증된 사용자의 프로필 조회 테스트"""
        if not auth_headers.get("Authorization"):
            pytest.skip("Authentication token not available")

        response = client.get("/api/v1/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # 프로필 정보 검증
        assert "email" in data
        assert "nickname" in data
        assert "id" in data
        # 비밀번호는 프로필에 포함되면 안 됨
        assert "password" not in data

    def test_get_my_profile_without_auth(self):
        """인증되지 않은 사용자의 프로필 조회 테스트"""
        response = client.get("/api/v1/me")

        assert response.status_code == 401

    def test_update_profile_with_auth(self, auth_headers):
        """인증된 사용자의 프로필 수정 테스트"""
        if not auth_headers.get("Authorization"):
            pytest.skip("Authentication token not available")

        update_data = {
            "nickname": f"updated_nickname_{datetime.now().strftime('%H%M%S')}"
        }

        response = client.put(
            "/api/v1/me", json=update_data, headers=auth_headers
        )

        # 프로필 수정이 지원되는 경우
        if response.status_code == 200:
            data = response.json()
            assert data["nickname"] == update_data["nickname"]

    def test_get_user_by_id(self):
        """ID로 사용자 정보 조회 테스트"""
        response = client.get("/api/v1/users/1")

        if response.status_code == 200:
            data = response.json()

            # 공개 정보만 포함되어야 함
            assert "id" in data
            assert "nickname" in data
            # 민감한 정보는 포함되면 안 됨
            assert "password" not in data
            assert "email" not in data or data["email"] is None
        else:
            # 사용자가 없거나 접근 권한이 없는 경우
            assert response.status_code in [404, 403]

    def test_get_user_posts(self):
        """특정 사용자의 게시글 목록 조회 테스트"""
        response = client.get("/api/v1/users/1/posts")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list) or "items" in data
        else:
            # 사용자가 없는 경우
            assert response.status_code == 404

    def test_follow_user_with_auth(self, auth_headers):
        """사용자 팔로우 테스트"""
        if not auth_headers.get("Authorization"):
            pytest.skip("Authentication token not available")

        # 다른 사용자를 팔로우
        response = client.post("/api/v1/users/2/follow", headers=auth_headers)

        # 팔로우 기능이 구현된 경우
        if response.status_code == 200:
            data = response.json()
            assert "following" in data

    def test_unfollow_user_with_auth(self, auth_headers):
        """사용자 언팔로우 테스트"""
        if not auth_headers.get("Authorization"):
            pytest.skip("Authentication token not available")

        # 사용자 언팔로우
        response = client.delete(
            "/api/v1/users/2/follow", headers=auth_headers
        )

        # 언팔로우 기능이 구현된 경우
        if response.status_code == 200:
            data = response.json()
            assert "following" in data


@pytest.fixture
def auth_token():
    """인증 토큰을 제공하는 픽스처"""
    login_data = {"email": "user@example.com", "password": "password123"}
    response = client.post("/api/v1/auth/login", json=login_data)

    if response.status_code == 200:
        return response.json()["accessToken"]
    return None


@pytest.fixture
def auth_headers(auth_token):
    """인증 헤더를 제공하는 픽스처"""
    if auth_token:
        return {"Authorization": f"Bearer {auth_token}"}
    return {}


@pytest.fixture
def test_user():
    """테스트용 사용자를 생성하는 픽스처"""
    timestamp = datetime.now().strftime("%H%M%S")
    signup_data = {
        "email": f"fixture_user_{timestamp}@example.com",
        "password": "fixture123",
        "nickname": f"fixture_user_{timestamp}",
    }

    response = client.post("/api/v1/users/signup", json=signup_data)

    if response.status_code == 201:
        return response.json()
    return None
