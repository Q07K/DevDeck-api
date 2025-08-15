"""
인증 API pytest 테스트

This module contains pytest-based tests for authentication endpoints.
"""

import pytest
from fastapi.testclient import TestClient

# Import your FastAPI app
from app.main import app

client = TestClient(app)

BASE_URL = "http://localhost:8000/api/v1"


class TestAuthAPI:
    """인증 API 테스트 클래스"""

    def test_login_success(self):
        """성공적인 로그인 테스트"""
        login_data = {"email": "user@example.com", "password": "password123"}

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert data["accessToken"] is not None

    def test_login_nonexistent_email(self):
        """존재하지 않는 이메일로 로그인 테스트"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123",
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401

    def test_login_wrong_password(self):
        """잘못된 비밀번호로 로그인 테스트"""
        login_data = {"email": "user@example.com", "password": "wrongpassword"}

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401

    def test_logout_with_token(self):
        """유효한 토큰으로 로그아웃 테스트"""
        # 먼저 로그인하여 토큰 획득
        login_data = {"email": "user@example.com", "password": "password123"}
        login_response = client.post("/api/v1/auth/login", json=login_data)

        if login_response.status_code == 200:
            token = login_response.json()["accessToken"]
            headers = {"Authorization": f"Bearer {token}"}

            # 로그아웃 테스트
            response = client.post("/api/v1/auth/logout", headers=headers)
            assert response.status_code == 200

    def test_logout_without_token(self):
        """토큰 없이 로그아웃 테스트"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401

    def test_protected_endpoint_without_token(self):
        """토큰 없이 보호된 엔드포인트 접근 테스트"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401


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
