from typing import List, Optional, Dict, Any
from datetime import datetime
import duckdb
from app.core.database import get_db_connection
from app.schemas.database_schemas import (
    UserCreate, UserUpdate, PostCreate, PostUpdate, 
    CommentCreate, CommentUpdate, TagCreate
)
import hashlib


class UserService:
    """사용자 관련 서비스"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """비밀번호 해싱"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def create_user(user_data: UserCreate) -> Dict[str, Any]:
        """사용자 생성"""
        conn = get_db_connection()
        hashed_password = UserService.hash_password(user_data.password)
        
        # DuckDB에서는 RETURNING을 지원하지 않으므로 INSERT 후 조회
        query = """
        INSERT INTO users (email, password, nickname)
        VALUES (?, ?, ?)
        """
        
        conn.execute(query, (user_data.email, hashed_password, user_data.nickname))
        
        # 방금 생성된 사용자 조회
        result = conn.execute("SELECT id, email, nickname, created_at, updated_at FROM users WHERE email = ?", 
                            (user_data.email,)).fetchone()
        
        return {
            "id": result[0],
            "email": result[1], 
            "nickname": result[2],
            "created_at": result[3],
            "updated_at": result[4]
        }
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """ID로 사용자 조회"""
        conn = get_db_connection()
        query = "SELECT id, email, nickname, created_at, updated_at FROM users WHERE id = ?"
        result = conn.execute(query, (user_id,)).fetchone()
        
        if result:
            return {
                "id": result[0],
                "email": result[1],
                "nickname": result[2], 
                "created_at": result[3],
                "updated_at": result[4]
            }
        return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """이메일로 사용자 조회"""
        conn = get_db_connection()
        query = "SELECT id, email, password, nickname, created_at, updated_at FROM users WHERE email = ?"
        result = conn.execute(query, (email,)).fetchone()
        
        if result:
            return {
                "id": result[0],
                "email": result[1],
                "password": result[2],
                "nickname": result[3],
                "created_at": result[4],
                "updated_at": result[5]
            }
        return None


class PostService:
    """게시글 관련 서비스"""
    
    @staticmethod
    def create_post(user_id: int, post_data: PostCreate) -> Dict[str, Any]:
        """게시글 생성"""
        conn = get_db_connection()
        
        # 게시글 생성 - DuckDB는 RETURNING을 지원하지 않음
        post_query = """
        INSERT INTO posts (user_id, title, content)
        VALUES (?, ?, ?)
        """
        
        conn.execute(post_query, (user_id, post_data.title, post_data.content))
        
        # 방금 생성된 게시글 조회 (가장 최근 생성된 것)
        post_result = conn.execute("""
            SELECT id, user_id, title, content, view_count, like_count, created_at, updated_at
            FROM posts 
            WHERE user_id = ? AND title = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id, post_data.title)).fetchone()
        
        post_id = post_result[0]
        
        # 태그 처리
        if post_data.tag_names:
            for tag_name in post_data.tag_names:
                # 태그가 없으면 생성
                tag_query = "INSERT INTO tags (name) VALUES (?) ON CONFLICT DO NOTHING"
                conn.execute(tag_query, (tag_name,))
                
                # 태그 ID 조회
                tag_id_query = "SELECT id FROM tags WHERE name = ?"
                tag_result = conn.execute(tag_id_query, (tag_name,)).fetchone()
                tag_id = tag_result[0]
                
                # 게시글-태그 연결
                post_tag_query = "INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?) ON CONFLICT DO NOTHING"
                conn.execute(post_tag_query, (post_id, tag_id))
        
        return {
            "id": post_result[0],
            "user_id": post_result[1],
            "title": post_result[2],
            "content": post_result[3],
            "view_count": post_result[4],
            "like_count": post_result[5],
            "created_at": post_result[6],
            "updated_at": post_result[7]
        }
    
    @staticmethod
    def get_post_by_id(post_id: int, increment_view: bool = False) -> Optional[Dict[str, Any]]:
        """ID로 게시글 조회"""
        conn = get_db_connection()
        
        # 조회수 증가
        if increment_view:
            conn.execute("UPDATE posts SET view_count = view_count + 1 WHERE id = ? AND deleted_at IS NULL", (post_id,))
        
        # 게시글 조회 (소프트 삭제된 글 제외)
        post_query = """
        SELECT p.id, p.user_id, p.title, p.content, p.view_count, p.like_count, 
               p.created_at, p.updated_at, p.deleted_at,
               u.nickname, u.email
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ? AND p.deleted_at IS NULL
        """
        
        post_result = conn.execute(post_query, (post_id,)).fetchone()
        if not post_result:
            return None
        
        # 태그 조회
        tags_query = """
        SELECT t.name
        FROM tags t
        JOIN post_tags pt ON t.id = pt.tag_id
        WHERE pt.post_id = ?
        """
        tags_result = conn.execute(tags_query, (post_id,)).fetchall()
        tags = [tag[0] for tag in tags_result]
        
        return {
            "id": post_result[0],
            "user_id": post_result[1], 
            "title": post_result[2],
            "content": post_result[3],
            "view_count": post_result[4],
            "like_count": post_result[5],
            "created_at": post_result[6],
            "updated_at": post_result[7],
            "deleted_at": post_result[8],
            "author": {
                "nickname": post_result[9],
                "email": post_result[10]
            },
            "tags": tags
        }
    
    @staticmethod
    def get_posts_list(page: int = 1, per_page: int = 10, tag_name: str = None) -> Dict[str, Any]:
        """게시글 목록 조회 (페이징)"""
        conn = get_db_connection()
        offset = (page - 1) * per_page
        
        # 기본 쿼리
        base_query = """
        SELECT p.id, p.title, p.user_id, p.view_count, p.like_count, p.created_at,
               u.nickname
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.deleted_at IS NULL
        """
        
        count_query = """
        SELECT COUNT(*)
        FROM posts p
        WHERE p.deleted_at IS NULL
        """
        
        params = []
        
        # 태그 필터링
        if tag_name:
            base_query += """
            AND p.id IN (
                SELECT pt.post_id
                FROM post_tags pt
                JOIN tags t ON pt.tag_id = t.id
                WHERE t.name = ?
            )
            """
            count_query += """
            AND p.id IN (
                SELECT pt.post_id
                FROM post_tags pt
                JOIN tags t ON pt.tag_id = t.id
                WHERE t.name = ?
            )
            """
            params.append(tag_name)
        
        # 정렬 및 페이징
        base_query += " ORDER BY p.created_at DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        
        # 결과 조회
        posts_result = conn.execute(base_query, params).fetchall()
        count_params = [tag_name] if tag_name else []
        total_result = conn.execute(count_query, count_params).fetchone()
        total = total_result[0]
        
        posts = []
        for post in posts_result:
            # 각 게시글의 태그 조회
            tags_query = """
            SELECT t.name
            FROM tags t
            JOIN post_tags pt ON t.id = pt.tag_id
            WHERE pt.post_id = ?
            """
            tags_result = conn.execute(tags_query, (post[0],)).fetchall()
            tags = [tag[0] for tag in tags_result]
            
            posts.append({
                "id": post[0],
                "title": post[1],
                "user_id": post[2],
                "author_nickname": post[6],
                "view_count": post[3],
                "like_count": post[4],
                "created_at": post[5],
                "tags": tags
            })
        
        return {
            "items": posts,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    @staticmethod
    def update_post(post_id: int, user_id: int, post_data: PostUpdate) -> Optional[Dict[str, Any]]:
        """게시글 수정"""
        conn = get_db_connection()
        
        # 권한 확인
        auth_query = "SELECT user_id FROM posts WHERE id = ? AND deleted_at IS NULL"
        auth_result = conn.execute(auth_query, (post_id,)).fetchone()
        if not auth_result or auth_result[0] != user_id:
            return None
        
        # 업데이트할 필드 구성
        update_fields = []
        params = []
        
        if post_data.title is not None:
            update_fields.append("title = ?")
            params.append(post_data.title)
        
        if post_data.content is not None:
            update_fields.append("content = ?")
            params.append(post_data.content)
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(post_id)
            
            update_query = f"UPDATE posts SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(update_query, params)
        
        # 태그 업데이트
        if post_data.tag_names is not None:
            # 기존 태그 연결 삭제
            conn.execute("DELETE FROM post_tags WHERE post_id = ?", (post_id,))
            
            # 새 태그 연결 추가
            for tag_name in post_data.tag_names:
                # 태그가 없으면 생성
                conn.execute("INSERT INTO tags (name) VALUES (?) ON CONFLICT DO NOTHING", (tag_name,))
                
                # 태그 ID 조회
                tag_result = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()
                tag_id = tag_result[0]
                
                # 게시글-태그 연결
                conn.execute("INSERT INTO post_tags (post_id, tag_id) VALUES (?, ?) ON CONFLICT DO NOTHING", (post_id, tag_id))
        
        return PostService.get_post_by_id(post_id)
    
    @staticmethod
    def delete_post(post_id: int, user_id: int) -> bool:
        """게시글 소프트 삭제"""
        conn = get_db_connection()
        
        # 권한 확인
        auth_query = "SELECT user_id FROM posts WHERE id = ? AND deleted_at IS NULL"
        auth_result = conn.execute(auth_query, (post_id,)).fetchone()
        if not auth_result or auth_result[0] != user_id:
            return False
        
        # 소프트 삭제
        delete_query = "UPDATE posts SET deleted_at = CURRENT_TIMESTAMP WHERE id = ?"
        conn.execute(delete_query, (post_id,))
        
        return True


class CommentService:
    """댓글 관련 서비스"""
    
    @staticmethod
    def create_comment(user_id: int, comment_data: CommentCreate) -> Dict[str, Any]:
        """댓글 생성"""
        conn = get_db_connection()
        
        # DuckDB는 RETURNING을 지원하지 않음
        query = """
        INSERT INTO comments (post_id, user_id, parent_comment_id, content)
        VALUES (?, ?, ?, ?)
        """
        
        conn.execute(query, (
            comment_data.post_id, 
            user_id, 
            comment_data.parent_comment_id, 
            comment_data.content
        ))
        
        # 방금 생성된 댓글 조회
        result = conn.execute("""
            SELECT id, post_id, user_id, parent_comment_id, content, created_at, updated_at
            FROM comments 
            WHERE post_id = ? AND user_id = ? AND content = ?
            ORDER BY created_at DESC 
            LIMIT 1
        """, (comment_data.post_id, user_id, comment_data.content)).fetchone()
        
        return {
            "id": result[0],
            "post_id": result[1],
            "user_id": result[2],
            "parent_comment_id": result[3],
            "content": result[4],
            "created_at": result[5],
            "updated_at": result[6]
        }
    
    @staticmethod
    def get_comments_by_post_id(post_id: int) -> List[Dict[str, Any]]:
        """게시글의 댓글 조회 (계층구조)"""
        conn = get_db_connection()
        
        query = """
        SELECT c.id, c.post_id, c.user_id, c.parent_comment_id, c.content, 
               c.created_at, c.updated_at, u.nickname
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.created_at ASC
        """
        
        results = conn.execute(query, (post_id,)).fetchall()
        
        # 댓글을 계층구조로 구성
        comments_map = {}
        root_comments = []
        
        for result in results:
            comment = {
                "id": result[0],
                "post_id": result[1],
                "user_id": result[2],
                "parent_comment_id": result[3],
                "content": result[4],
                "created_at": result[5],
                "updated_at": result[6],
                "author_nickname": result[7],
                "replies": []
            }
            
            comments_map[comment["id"]] = comment
            
            if comment["parent_comment_id"] is None:
                root_comments.append(comment)
            else:
                parent = comments_map.get(comment["parent_comment_id"])
                if parent:
                    parent["replies"].append(comment)
        
        return root_comments


class PostLikeService:
    """게시글 좋아요 관련 서비스"""
    
    @staticmethod
    def toggle_like(user_id: int, post_id: int) -> Dict[str, Any]:
        """좋아요 토글 (좋아요/취소)"""
        conn = get_db_connection()
        
        # 이미 좋아요했는지 확인
        check_query = "SELECT 1 FROM post_likes WHERE user_id = ? AND post_id = ?"
        existing = conn.execute(check_query, (user_id, post_id)).fetchone()
        
        if existing:
            # 좋아요 취소
            conn.execute("DELETE FROM post_likes WHERE user_id = ? AND post_id = ?", (user_id, post_id))
            conn.execute("UPDATE posts SET like_count = like_count - 1 WHERE id = ?", (post_id,))
            action = "unliked"
        else:
            # 좋아요 추가
            conn.execute("INSERT INTO post_likes (user_id, post_id) VALUES (?, ?)", (user_id, post_id))
            conn.execute("UPDATE posts SET like_count = like_count + 1 WHERE id = ?", (post_id,))
            action = "liked"
        
        # 현재 좋아요 수 조회
        like_count_query = "SELECT like_count FROM posts WHERE id = ?"
        like_count_result = conn.execute(like_count_query, (post_id,)).fetchone()
        
        return {
            "action": action,
            "like_count": like_count_result[0] if like_count_result else 0
        }


class TagService:
    """태그 관련 서비스"""
    
    @staticmethod
    def get_all_tags() -> List[Dict[str, Any]]:
        """모든 태그 조회"""
        conn = get_db_connection()
        
        query = """
        SELECT t.id, t.name, COUNT(pt.post_id) as post_count
        FROM tags t
        LEFT JOIN post_tags pt ON t.id = pt.tag_id
        LEFT JOIN posts p ON pt.post_id = p.id AND p.deleted_at IS NULL
        GROUP BY t.id, t.name
        ORDER BY post_count DESC, t.name ASC
        """
        
        results = conn.execute(query).fetchall()
        
        return [
            {
                "id": result[0],
                "name": result[1],
                "post_count": result[2]
            }
            for result in results
        ]
