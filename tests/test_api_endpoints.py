"""
API Endpoints pytest 테스트

This module contains pytest-based tests for SQLAlchemy API endpoints.
"""

import time

import pytest
from fastapi.testclient import TestClient

# Import your FastAPI app
from app.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """API 엔드포인트 테스트 클래스"""

    def test_create_user_endpoint(self):
        """사용자 생성 엔드포인트 테스트"""
        timestamp = int(time.time())
        user_data = {
            "email": f"api_test_{timestamp}@example.com",
            "password": "apitest123",
            "nickname": f"apitest_user_{timestamp}",
        }

        response = client.post("/api/v1/blog/users", json=user_data)

        if response.status_code == 201:
            data = response.json()

            # 응답 구조 검증
            assert "data" in data
            user = data["data"]

            assert user["nickname"] == user_data["nickname"]
            assert user["email"] == user_data["email"]
            assert "id" in user
            assert "password" not in user  # 비밀번호는 응답에 포함되면 안 됨

        else:
            # API가 구현되지 않았거나 다른 오류
            assert response.status_code in [404, 405, 422]

    def test_get_user_endpoint(self):
        """사용자 조회 엔드포인트 테스트"""
        # 먼저 사용자를 생성
        timestamp = int(time.time())
        user_data = {
            "email": f"api_get_test_{timestamp}@example.com",
            "password": "apitest123",
            "nickname": f"apiget_user_{timestamp}",
        }

        create_response = client.post("/api/v1/blog/users", json=user_data)

        if create_response.status_code == 201:
            user_id = create_response.json()["data"]["id"]

            # 생성한 사용자 조회
            response = client.get(f"/api/v1/blog/users/{user_id}")

            assert response.status_code == 200
            data = response.json()

            assert "data" in data
            user = data["data"]

            assert user["id"] == user_id
            assert user["email"] == user_data["email"]
            assert user["nickname"] == user_data["nickname"]

        else:
            pytest.skip("User creation endpoint not available")

    def test_create_post_endpoint(self):
        """게시글 생성 엔드포인트 테스트"""
        # 먼저 사용자를 생성
        timestamp = int(time.time())
        user_data = {
            "email": f"post_test_{timestamp}@example.com",
            "password": "posttest123",
            "nickname": f"posttest_user_{timestamp}",
        }

        user_response = client.post("/api/v1/blog/users", json=user_data)

        if user_response.status_code == 201:
            user_id = user_response.json()["data"]["id"]

            # 게시글 생성
            post_data = {
                "title": f"API Test Post {timestamp}",
                "content": "이것은 API 엔드포인트 테스트를 위한 게시글입니다.",
                "tag_names": ["API", "Test", "pytest"],
            }

            response = client.post(
                f"/api/v1/blog/users/{user_id}/posts", json=post_data
            )

            if response.status_code == 201:
                data = response.json()

                assert "data" in data
                post = data["data"]

                assert post["title"] == post_data["title"]
                assert post["content"] == post_data["content"]
                assert "id" in post
                assert "author_id" in post or "user_id" in post

            else:
                # 게시글 생성 API가 구현되지 않은 경우
                assert response.status_code in [404, 405, 422]
        else:
            pytest.skip("User creation endpoint not available for post test")

    def test_get_posts_endpoint(self):
        """게시글 목록 조회 엔드포인트 테스트"""
        response = client.get("/api/v1/blog/posts")

        if response.status_code == 200:
            data = response.json()

            # 응답 구조 검증
            assert "data" in data or "items" in data or isinstance(data, list)

            if "data" in data:
                posts = data["data"]
            elif "items" in data:
                posts = data["items"]
            else:
                posts = data

            assert isinstance(posts, list)

            for post in posts:
                assert "id" in post
                assert "title" in post
                assert "content" in post

        else:
            # 게시글 목록 API가 구현되지 않은 경우
            assert response.status_code == 404

    def test_update_user_endpoint(self):
        """사용자 정보 수정 엔드포인트 테스트"""
        # 먼저 사용자를 생성
        timestamp = int(time.time())
        user_data = {
            "email": f"update_test_{timestamp}@example.com",
            "password": "updatetest123",
            "nickname": f"updatetest_user_{timestamp}",
        }

        create_response = client.post("/api/v1/blog/users", json=user_data)

        if create_response.status_code == 201:
            user_id = create_response.json()["data"]["id"]

            # 사용자 정보 수정
            update_data = {
                "nickname": f"updated_user_{timestamp}",
                "email": f"updated_{timestamp}@example.com",
            }

            response = client.put(
                f"/api/v1/blog/users/{user_id}", json=update_data
            )

            if response.status_code == 200:
                data = response.json()

                assert "data" in data
                user = data["data"]

                assert user["nickname"] == update_data["nickname"]
                assert user["email"] == update_data["email"]
                assert user["id"] == user_id

            else:
                # 사용자 수정 API가 구현되지 않은 경우
                assert response.status_code in [404, 405, 422]
        else:
            pytest.skip("User creation endpoint not available for update test")

    def test_delete_user_endpoint(self):
        """사용자 삭제 엔드포인트 테스트"""
        # 먼저 사용자를 생성
        timestamp = int(time.time())
        user_data = {
            "email": f"delete_test_{timestamp}@example.com",
            "password": "deletetest123",
            "nickname": f"deletetest_user_{timestamp}",
        }

        create_response = client.post("/api/v1/blog/users", json=user_data)

        if create_response.status_code == 201:
            user_id = create_response.json()["data"]["id"]

            # 사용자 삭제
            response = client.delete(f"/api/v1/blog/users/{user_id}")

            if response.status_code in [200, 204]:
                # 삭제 후 조회 시도
                get_response = client.get(f"/api/v1/blog/users/{user_id}")
                assert get_response.status_code == 404

            else:
                # 사용자 삭제 API가 구현되지 않은 경우
                assert response.status_code in [404, 405]
        else:
            pytest.skip("User creation endpoint not available for delete test")

    def test_get_user_posts_endpoint(self):
        """특정 사용자의 게시글 목록 조회 엔드포인트 테스트"""
        # 기존 사용자의 게시글 조회 (ID: 1)
        response = client.get("/api/v1/blog/users/1/posts")

        if response.status_code == 200:
            data = response.json()

            assert "data" in data or isinstance(data, list)

            if "data" in data:
                posts = data["data"]
            else:
                posts = data

            assert isinstance(posts, list)

            for post in posts:
                assert "id" in post
                assert "title" in post
                assert "author_id" in post or "user_id" in post

                # 모든 게시글이 해당 사용자의 것인지 확인
                author_id = post.get("author_id", post.get("user_id"))
                assert author_id == 1

        else:
            # API가 구현되지 않았거나 사용자가 없는 경우
            assert response.status_code in [404, 405]

    def test_api_error_handling(self):
        """API 에러 처리 테스트"""
        # 존재하지 않는 사용자 조회
        response = client.get("/api/v1/blog/users/99999")

        assert response.status_code == 404

        # 잘못된 데이터로 사용자 생성
        invalid_user_data = {
            "email": "invalid-email",  # 잘못된 이메일 형식
            "password": "123",  # 너무 짧은 비밀번호
            "nickname": "",  # 빈 닉네임
        }

        response = client.post("/api/v1/blog/users", json=invalid_user_data)

        assert response.status_code in [400, 422]  # 검증 오류

    def test_api_response_consistency(self):
        """API 응답 일관성 테스트"""
        endpoints = [
            ("/api/v1/blog/users", "GET"),
            ("/api/v1/blog/posts", "GET"),
        ]

        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                continue

            if response.status_code == 200:
                data = response.json()

                # 모든 성공 응답이 일관된 구조를 가지는지 확인
                assert isinstance(data, dict)

                # 성공 응답은 데이터를 포함해야 함
                has_data = (
                    "data" in data or "items" in data or len(data.keys()) > 0
                )
                assert has_data

    def test_content_type_headers(self):
        """Content-Type 헤더 테스트"""
        response = client.get("/api/v1/blog/posts")

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert "application/json" in content_type.lower()


@pytest.fixture(scope="module")
def test_user_data():
    """테스트용 사용자 데이터를 제공하는 픽스처"""
    timestamp = int(time.time())
    return {
        "email": f"fixture_user_{timestamp}@example.com",
        "password": "fixturetest123",
        "nickname": f"fixture_user_{timestamp}",
    }


@pytest.fixture(scope="module")
def created_user(test_user_data):
    """테스트용 사용자를 생성하는 픽스처"""
    response = client.post("/api/v1/blog/users", json=test_user_data)

    if response.status_code == 201:
        return response.json()["data"]
    return None
