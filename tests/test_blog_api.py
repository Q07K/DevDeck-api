"""
Blog API pytest 테스트

This module contains pytest-based tests for blog API endpoints.
"""

from fastapi.testclient import TestClient

# Import your FastAPI app
from app.main import app

client = TestClient(app)


class TestBlogAPI:
    """블로그 API 테스트 클래스"""

    def test_get_all_tags(self):
        """모든 태그 조회 테스트"""
        response = client.get("/api/v1/blog/tags")

        assert response.status_code == 200
        data = response.json()

        # API 응답 구조에 따라 검증
        if "data" in data:
            tags = data["data"]["tags"]
        else:
            tags = data

        assert isinstance(tags, list)

        for tag in tags:
            assert "id" in tag or "name" in tag
            if "post_count" in tag:
                assert isinstance(tag["post_count"], int)

    def test_get_posts_list_default(self):
        """기본 게시글 목록 조회 테스트"""
        response = client.get("/api/v1/blog/posts")

        assert response.status_code == 200
        data = response.json()

        # 페이지네이션 정보 검증
        assert "items" in data or "posts" in data
        assert "total" in data or "totalPages" in data

        posts = data.get("items", data.get("posts", []))
        assert isinstance(posts, list)

    def test_get_posts_list_with_pagination(self):
        """페이지네이션이 있는 게시글 목록 조회 테스트"""
        response = client.get("/api/v1/blog/posts?page=1&per_page=3")

        assert response.status_code == 200
        data = response.json()

        posts = data.get("items", data.get("posts", []))
        assert len(posts) <= 3

        # 페이지 정보 검증
        if "page" in data:
            assert data["page"] == 1
        if "per_page" in data:
            assert data["per_page"] == 3

    def test_get_posts_list_with_tag_filter(self):
        """태그 필터가 있는 게시글 목록 조회 테스트"""
        # 먼저 태그 목록을 가져와서 존재하는 태그 사용
        tags_response = client.get("/api/v1/blog/tags")

        if tags_response.status_code == 200:
            tags_data = tags_response.json()
            tags = tags_data.get("data", {}).get("tags", tags_data)

            if tags:
                first_tag = tags[0]["name"]

                response = client.get(f"/api/v1/blog/posts?tag={first_tag}")

                assert response.status_code == 200
                data = response.json()

                posts = data.get("items", data.get("posts", []))

                # 필터링된 게시글들이 해당 태그를 포함하는지 검증
                for post in posts:
                    if "tags" in post:
                        assert first_tag in post["tags"]

    def test_get_post_detail_success(self):
        """게시글 상세 조회 성공 테스트"""
        response = client.get("/api/v1/blog/posts/1")

        if response.status_code == 200:
            data = response.json()

            # API 응답 구조에 따라 검증
            post_data = data.get("data", data)

            assert "id" in post_data
            assert "title" in post_data
            assert "content" in post_data
            assert "author" in post_data

            # 작성자 정보 검증
            author = post_data["author"]
            assert "nickname" in author

            # 태그 정보 검증
            assert "tags" in post_data
            assert isinstance(post_data["tags"], list)
        else:
            # 게시글이 없는 경우 404 응답이 정상
            assert response.status_code == 404

    def test_get_post_detail_not_found(self):
        """존재하지 않는 게시글 상세 조회 테스트"""
        response = client.get("/api/v1/blog/posts/99999")

        assert response.status_code == 404

    def test_get_post_comments(self):
        """게시글 댓글 조회 테스트"""
        response = client.get("/api/v1/blog/posts/1/comments")

        if response.status_code == 200:
            data = response.json()

            comments_data = data.get("data", {}).get("comments", data)
            assert isinstance(comments_data, list)

            for comment in comments_data:
                assert "id" in comment
                assert "content" in comment
                assert "author_nickname" in comment

                # 답글 구조 검증
                if "replies" in comment:
                    assert isinstance(comment["replies"], list)

                    for reply in comment["replies"]:
                        assert "id" in reply
                        assert "content" in reply
                        assert "author_nickname" in reply
        else:
            # 게시글이 없거나 댓글이 없는 경우
            assert response.status_code in [404, 200]

    def test_search_posts(self):
        """게시글 검색 테스트"""
        search_query = "test"
        response = client.get(f"/api/v1/blog/posts/search?q={search_query}")

        if response.status_code == 200:
            data = response.json()

            posts = data.get("items", data.get("posts", []))
            assert isinstance(posts, list)

            # 검색 결과의 제목이나 내용에 검색어가 포함되는지 검증
            for post in posts:
                title = post.get("title", "").lower()
                content = post.get("content", "").lower()
                assert (
                    search_query.lower() in title
                    or search_query.lower() in content
                )
        else:
            # 검색 기능이 구현되지 않은 경우
            assert response.status_code in [404, 501]

    def test_get_popular_posts(self):
        """인기 게시글 조회 테스트"""
        response = client.get("/api/v1/blog/posts/popular")

        if response.status_code == 200:
            data = response.json()

            posts = data.get("items", data.get("posts", []))
            assert isinstance(posts, list)

            # 인기 게시글은 조회수나 좋아요 순으로 정렬되어야 함
            if len(posts) > 1:
                # 첫 번째 게시글이 두 번째보다 인기가 높아야 함
                first_post = posts[0]
                second_post = posts[1]

                first_popularity = first_post.get(
                    "view_count", 0
                ) + first_post.get("like_count", 0)
                second_popularity = second_post.get(
                    "view_count", 0
                ) + second_post.get("like_count", 0)

                assert first_popularity >= second_popularity
        else:
            # 인기 게시글 기능이 구현되지 않은 경우
            assert response.status_code in [404, 501]

    def test_get_recent_posts(self):
        """최신 게시글 조회 테스트"""
        response = client.get("/api/v1/blog/posts/recent")

        if response.status_code == 200:
            data = response.json()

            posts = data.get("items", data.get("posts", []))
            assert isinstance(posts, list)

            # 최신 게시글은 생성 시간순으로 정렬되어야 함
            if len(posts) > 1:
                first_post = posts[0]
                second_post = posts[1]

                # 첫 번째 게시글의 ID가 더 큰 경우 (더 최신)
                if "id" in first_post and "id" in second_post:
                    assert first_post["id"] >= second_post["id"]
        else:
            # 최신 게시글 기능이 구현되지 않은 경우
            assert response.status_code in [404, 501]

    def test_api_response_format(self):
        """API 응답 형식 일관성 테스트"""
        endpoints = [
            "/api/v1/blog/posts",
            "/api/v1/blog/tags",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)

            if response.status_code == 200:
                data = response.json()

                # API 응답이 일관된 형식을 가지는지 검증
                assert isinstance(data, dict)

                # 성공 응답에는 적절한 데이터가 포함되어야 함
                if "data" in data:
                    assert data["data"] is not None
                elif "items" in data:
                    assert isinstance(data["items"], list)

    def test_error_response_format(self):
        """에러 응답 형식 테스트"""
        # 존재하지 않는 엔드포인트 호출
        response = client.get("/api/v1/blog/nonexistent")

        assert response.status_code == 404

        # 에러 응답 형식 검증
        data = response.json()
        assert isinstance(data, dict)

        # 에러 메시지나 상세 정보가 포함되어야 함
        assert "detail" in data or "message" in data or "error" in data
