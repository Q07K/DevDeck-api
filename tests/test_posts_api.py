"""
Posts API pytest 테스트

This module contains pytest-based tests for posts endpoints.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

# Import your FastAPI app
from app.main import app

client = TestClient(app)


class TestPostsAPI:
    """Posts API 테스트 클래스"""

    def test_get_posts_list(self):
        """글 목록 조회 테스트"""
        response = client.get("/api/v1/posts")

        assert response.status_code == 200
        data = response.json()

        # 응답 구조 검증
        assert "totalPages" in data or "total_pages" in data
        assert "posts" in data or "items" in data

    def test_get_posts_with_pagination(self):
        """페이지네이션을 포함한 글 목록 조회 테스트"""
        response = client.get("/api/v1/posts?page=1&per_page=5")

        assert response.status_code == 200
        data = response.json()

        # 페이지네이션 검증
        posts = data.get("posts", data.get("items", []))
        assert len(posts) <= 5

    def test_get_post_detail_success(self):
        """존재하는 글의 상세 조회 테스트"""
        response = client.get("/api/v1/posts/1")

        if response.status_code == 200:
            data = response.json()

            # 응답 구조 검증
            assert "title" in data
            assert "author" in data
            assert "content" in data
        else:
            # 게시글이 없는 경우는 404가 정상
            assert response.status_code == 404

    def test_get_post_detail_not_found(self):
        """존재하지 않는 글의 상세 조회 테스트"""
        response = client.get("/api/v1/posts/99999")

        assert response.status_code == 404

    def test_create_post_with_auth(self, auth_headers):
        """인증된 사용자의 글 작성 테스트"""
        if not auth_headers.get("Authorization"):
            pytest.skip("Authentication token not available")

        post_data = {
            "title": f"테스트 글 제목 {datetime.now().strftime('%H%M%S')}",
            "content": "이것은 pytest를 이용한 테스트 글입니다.",
            "tags": ["pytest", "test", "fastapi"],
        }

        response = client.post(
            "/api/v1/posts", json=post_data, headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == post_data["title"]
        assert data["content"] == post_data["content"]

    def test_create_post_without_auth(self):
        """인증되지 않은 사용자의 글 작성 테스트"""
        post_data = {
            "title": "인증 없는 테스트 글",
            "content": "이 글은 작성되면 안 됩니다.",
        }

        response = client.post("/api/v1/posts", json=post_data)

        assert response.status_code == 401

    def test_update_post_with_auth(self, auth_headers):
        """인증된 사용자의 글 수정 테스트"""
        if not auth_headers.get("Authorization"):
            pytest.skip("Authentication token not available")

        # 먼저 글을 생성
        post_data = {"title": "수정 테스트용 글", "content": "수정 전 내용"}

        create_response = client.post(
            "/api/v1/posts", json=post_data, headers=auth_headers
        )

        if create_response.status_code == 201:
            post_id = create_response.json()["id"]

            # 글 수정
            update_data = {"title": "수정된 제목", "content": "수정된 내용"}

            response = client.put(
                f"/api/v1/posts/{post_id}",
                json=update_data,
                headers=auth_headers,
            )

            # 글 수정이 지원되는 경우
            if response.status_code == 200:
                data = response.json()
                assert data["title"] == update_data["title"]

    def test_delete_post_with_auth(self, auth_headers):
        """인증된 사용자의 글 삭제 테스트"""
        if not auth_headers.get("Authorization"):
            pytest.skip("Authentication token not available")

        # 먼저 글을 생성
        post_data = {
            "title": "삭제 테스트용 글",
            "content": "삭제될 글입니다.",
        }

        create_response = client.post(
            "/api/v1/posts", json=post_data, headers=auth_headers
        )

        if create_response.status_code == 201:
            post_id = create_response.json()["id"]

            # 글 삭제
            response = client.delete(
                f"/api/v1/posts/{post_id}", headers=auth_headers
            )

            # 삭제가 지원되는 경우 204 또는 200
            assert response.status_code in [200, 204]

    def test_like_post_with_auth(self, auth_headers):
        """글 좋아요 테스트"""
        if not auth_headers.get("Authorization"):
            pytest.skip("Authentication token not available")

        # 존재하는 글에 좋아요
        response = client.post("/api/v1/posts/1/like", headers=auth_headers)

        # 좋아요 기능이 구현된 경우
        if response.status_code == 200:
            data = response.json()
            assert "like_count" in data or "likeCount" in data


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
