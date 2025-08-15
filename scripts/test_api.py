"""
DuckDB 블로그 API 테스트 스크립트

이 스크립트는 FastAPI 서버가 실행 중일 때 모든 API 엔드포인트를 테스트합니다.
"""

import requests
import json
from typing import Dict, Any


class BlogAPITester:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1/blog"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_get_all_tags(self) -> Dict[str, Any]:
        """모든 태그 조회 테스트"""
        print("🏷️ 태그 목록 조회 테스트...")
        response = self.session.get(f"{self.base_url}/tags")
        
        if response.status_code == 200:
            data = response.json()
            tags = data['data']['tags']
            print(f"✓ 성공: {len(tags)}개 태그 조회")
            for tag in tags[:3]:  # 처음 3개만 출력
                print(f"  - {tag['name']} ({tag['post_count']}개 게시글)")
            return data
        else:
            print(f"✗ 실패: {response.status_code} - {response.text}")
            return {}
    
    def test_get_posts_list(self, page: int = 1, per_page: int = 5, tag: str = None) -> Dict[str, Any]:
        """게시글 목록 조회 테스트"""
        params = {"page": page, "per_page": per_page}
        if tag:
            params["tag"] = tag
        
        filter_text = f" (태그: {tag})" if tag else ""
        print(f"📝 게시글 목록 조회 테스트{filter_text}...")
        
        response = self.session.get(f"{self.base_url}/posts", params=params)
        
        if response.status_code == 200:
            data = response.json()
            posts = data['items']
            print(f"✓ 성공: 총 {data['total']}개 중 {len(posts)}개 게시글 조회")
            print(f"  페이지: {data['page']}/{data['total_pages']}")
            
            for post in posts:
                tags_text = ", ".join(post['tags']) if post['tags'] else "태그 없음"
                print(f"  - [{post['id']}] {post['title'][:30]}... (👀{post['view_count']} ❤️{post['like_count']}) [{tags_text}]")
            
            return data
        else:
            print(f"✗ 실패: {response.status_code} - {response.text}")
            return {}
    
    def test_get_post_detail(self, post_id: int) -> Dict[str, Any]:
        """게시글 상세 조회 테스트"""
        print(f"📖 게시글 상세 조회 테스트 (ID: {post_id})...")
        
        response = self.session.get(f"{self.base_url}/posts/{post_id}")
        
        if response.status_code == 200:
            data = response.json()
            post = data['data']
            print(f"✓ 성공: '{post['title']}'")
            print(f"  작성자: {post['author']['nickname']}")
            print(f"  태그: {', '.join(post['tags']) if post['tags'] else '없음'}")
            print(f"  조회수: {post['view_count']}, 좋아요: {post['like_count']}")
            print(f"  내용: {post['content'][:100]}...")
            
            return data
        else:
            print(f"✗ 실패: {response.status_code} - {response.text}")
            return {}
    
    def test_get_post_comments(self, post_id: int) -> Dict[str, Any]:
        """게시글 댓글 조회 테스트"""
        print(f"💬 댓글 조회 테스트 (게시글 ID: {post_id})...")
        
        response = self.session.get(f"{self.base_url}/posts/{post_id}/comments")
        
        if response.status_code == 200:
            data = response.json()
            comments = data['data']['comments']
            print(f"✓ 성공: {len(comments)}개 최상위 댓글 조회")
            
            def print_comment(comment, depth=0):
                indent = "  " * depth
                print(f"{indent}- {comment['author_nickname']}: {comment['content'][:50]}...")
                for reply in comment['replies']:
                    print_comment(reply, depth + 1)
            
            for comment in comments:
                print_comment(comment)
            
            return data
        else:
            print(f"✗ 실패: {response.status_code} - {response.text}")
            return {}
    
    def test_create_user(self, email: str, nickname: str, password: str) -> Dict[str, Any]:
        """사용자 생성 테스트"""
        print(f"👤 사용자 생성 테스트 ({nickname})...")
        
        user_data = {
            "email": email,
            "nickname": nickname,
            "password": password
        }
        
        response = self.session.post(f"{self.base_url}/users", json=user_data)
        
        if response.status_code == 201:
            data = response.json()
            user = data['data']
            print(f"✓ 성공: 사용자 '{user['nickname']}' 생성 (ID: {user['id']})")
            return data
        else:
            print(f"✗ 실패: {response.status_code} - {response.text}")
            return {}
    
    def test_create_post(self, title: str, content: str, tag_names: list = None) -> Dict[str, Any]:
        """게시글 생성 테스트"""
        print(f"📝 게시글 생성 테스트 ('{title[:20]}...')...")
        
        post_data = {
            "title": title,
            "content": content,
            "tag_names": tag_names or []
        }
        
        response = self.session.post(f"{self.base_url}/posts", json=post_data)
        
        if response.status_code == 201:
            data = response.json()
            post = data['data']
            print(f"✓ 성공: 게시글 생성 (ID: {post['id']})")
            return data
        else:
            print(f"✗ 실패: {response.status_code} - {response.text}")
            return {}
    
    def test_create_comment(self, post_id: int, content: str, parent_comment_id: int = None) -> Dict[str, Any]:
        """댓글 생성 테스트"""
        comment_type = "대댓글" if parent_comment_id else "댓글"
        print(f"💬 {comment_type} 생성 테스트...")
        
        comment_data = {
            "post_id": post_id,
            "content": content,
            "parent_comment_id": parent_comment_id
        }
        
        response = self.session.post(f"{self.base_url}/comments", json=comment_data)
        
        if response.status_code == 201:
            data = response.json()
            comment = data['data']
            print(f"✓ 성공: {comment_type} 생성 (ID: {comment['id']})")
            return data
        else:
            print(f"✗ 실패: {response.status_code} - {response.text}")
            return {}
    
    def test_toggle_post_like(self, post_id: int) -> Dict[str, Any]:
        """게시글 좋아요 토글 테스트"""
        print(f"❤️ 좋아요 토글 테스트 (게시글 ID: {post_id})...")
        
        response = self.session.post(f"{self.base_url}/posts/{post_id}/like")
        
        if response.status_code == 200:
            data = response.json()
            result = data['data']
            action_text = "좋아요" if result['action'] == 'liked' else "좋아요 취소"
            print(f"✓ 성공: {action_text} (현재 좋아요 수: {result['like_count']})")
            return data
        else:
            print(f"✗ 실패: {response.status_code} - {response.text}")
            return {}
    
    def run_comprehensive_test(self):
        """포괄적인 API 테스트 실행"""
        print("🚀 DuckDB 블로그 API 종합 테스트 시작\n")
        print("=" * 60)
        
        try:
            # 1. 태그 목록 조회
            print("\n1️⃣ 태그 관련 테스트")
            print("-" * 30)
            self.test_get_all_tags()
            
            # 2. 게시글 목록 조회
            print("\n2️⃣ 게시글 목록 테스트")
            print("-" * 30)
            posts_data = self.test_get_posts_list(page=1, per_page=3)
            
            # 특정 태그로 필터링
            if posts_data and posts_data['items']:
                # 첫 번째 게시글의 태그로 필터링 테스트
                first_post = posts_data['items'][0]
                if first_post['tags']:
                    tag_name = first_post['tags'][0]
                    self.test_get_posts_list(page=1, per_page=2, tag=tag_name)
            
            # 3. 게시글 상세 조회
            print("\n3️⃣ 게시글 상세 조회 테스트")
            print("-" * 30)
            if posts_data and posts_data['items']:
                first_post_id = posts_data['items'][0]['id']
                post_detail = self.test_get_post_detail(first_post_id)
                
                # 4. 댓글 조회
                print("\n4️⃣ 댓글 조회 테스트")
                print("-" * 30)
                self.test_get_post_comments(first_post_id)
                
                # 5. 좋아요 토글 테스트
                print("\n5️⃣ 좋아요 기능 테스트")
                print("-" * 30)
                # 좋아요 추가
                self.test_toggle_post_like(first_post_id)
                # 좋아요 제거
                self.test_toggle_post_like(first_post_id)
            
            # 6. 게시글 생성 테스트
            print("\n6️⃣ 게시글 생성 테스트")
            print("-" * 30)
            new_post_data = self.test_create_post(
                title="API 테스트로 생성된 게시글",
                content="이 게시글은 DuckDB API 테스트를 통해 생성되었습니다.\n\n여러 줄의 내용을 포함하고 있습니다.",
                tag_names=["API테스트", "DuckDB", "자동생성"]
            )
            
            # 7. 댓글 생성 테스트
            if new_post_data and 'data' in new_post_data:
                new_post_id = new_post_data['data']['id']
                
                print("\n7️⃣ 댓글 생성 테스트")
                print("-" * 30)
                # 일반 댓글 생성
                comment_data = self.test_create_comment(
                    post_id=new_post_id,
                    content="API 테스트로 생성된 댓글입니다."
                )
                
                # 대댓글 생성
                if comment_data and 'data' in comment_data:
                    parent_comment_id = comment_data['data']['id']
                    self.test_create_comment(
                        post_id=new_post_id,
                        content="API 테스트로 생성된 대댓글입니다.",
                        parent_comment_id=parent_comment_id
                    )
            
            print("\n" + "=" * 60)
            print("🎉 모든 API 테스트가 완료되었습니다!")
            
        except requests.exceptions.ConnectionError:
            print("❌ 서버에 연결할 수 없습니다.")
            print("FastAPI 서버가 실행 중인지 확인해주세요: uvicorn main:app --reload")
        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {str(e)}")


def main():
    print("DuckDB 블로그 API 테스트")
    print("=" * 40)
    
    base_url = input("API 서버 URL을 입력하세요 (기본값: http://localhost:8000/api/v1/blog): ").strip()
    if not base_url:
        base_url = "http://localhost:8000/api/v1/blog"
    
    tester = BlogAPITester(base_url)
    
    print(f"\n📡 서버 URL: {base_url}")
    print("📋 종합 테스트를 시작합니다...\n")
    
    tester.run_comprehensive_test()


if __name__ == "__main__":
    main()
