import duckdb
from typing import Optional
from app.core.config import settings
import os


class DuckDBManager:
    """DuckDB 데이터베이스 매니저"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DUCKDB_FILE
        self._connection: Optional[duckdb.DuckDBPyConnection] = None
    
    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """DuckDB 연결 반환"""
        if self._connection is None:
            self._connection = duckdb.connect(self.db_path)
        return self._connection
    
    def close_connection(self):
        """연결 종료"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def execute_query(self, query: str, parameters: tuple = None):
        """쿼리 실행"""
        conn = self.get_connection()
        try:
            if parameters:
                return conn.execute(query, parameters).fetchall()
            else:
                return conn.execute(query).fetchall()
        except Exception as e:
            print(f"Query execution error: {e}")
            raise
    
    def execute_script(self, script: str):
        """스크립트 실행 (여러 쿼리)"""
        conn = self.get_connection()
        try:
            # DuckDB는 executescript가 없으므로 세미콜론으로 분할해서 실행
            statements = [stmt.strip() for stmt in script.split(';') if stmt.strip()]
            for statement in statements:
                if statement:
                    conn.execute(statement)
        except Exception as e:
            print(f"Script execution error: {e}")
            raise
    
    def create_tables(self):
        """ERD에 따른 모든 테이블 생성"""
        create_tables_script = """
        -- 기존 테이블 삭제
        DROP TABLE IF EXISTS post_likes;
        DROP TABLE IF EXISTS post_tags;
        DROP TABLE IF EXISTS comments;
        DROP TABLE IF EXISTS posts;
        DROP TABLE IF EXISTS tags;
        DROP TABLE IF EXISTS users;
        
        -- 시퀀스 생성 (DuckDB 방식)
        CREATE SEQUENCE IF NOT EXISTS users_id_seq;
        CREATE SEQUENCE IF NOT EXISTS posts_id_seq;
        CREATE SEQUENCE IF NOT EXISTS tags_id_seq;
        CREATE SEQUENCE IF NOT EXISTS comments_id_seq;
        
        -- Users 테이블 생성
        CREATE TABLE users (
            id INTEGER PRIMARY KEY DEFAULT nextval('users_id_seq'),
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            nickname VARCHAR(50) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Posts 테이블 생성
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY DEFAULT nextval('posts_id_seq'),
            user_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            view_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        
        -- Tags 테이블 생성
        CREATE TABLE tags (
            id INTEGER PRIMARY KEY DEFAULT nextval('tags_id_seq'),
            name VARCHAR(50) UNIQUE NOT NULL
        );
        
        -- Comments 테이블 생성
        CREATE TABLE comments (
            id INTEGER PRIMARY KEY DEFAULT nextval('comments_id_seq'),
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            parent_comment_id INTEGER NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (parent_comment_id) REFERENCES comments(id)
        );
        
        -- Post_Tags 연결 테이블 생성 (다대다 관계)
        CREATE TABLE post_tags (
            post_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (post_id, tag_id),
            FOREIGN KEY (post_id) REFERENCES posts(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        );
        
        -- Post_Likes 연결 테이블 생성 (다대다 관계)
        CREATE TABLE post_likes (
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, post_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (post_id) REFERENCES posts(id)
        );
        
        -- 인덱스 생성 (성능 최적화)
        CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
        CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at);
        CREATE INDEX IF NOT EXISTS idx_posts_deleted_at ON posts(deleted_at);
        CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);
        CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id);
        CREATE INDEX IF NOT EXISTS idx_comments_parent_id ON comments(parent_comment_id);
        """
        
        self.execute_script(create_tables_script)
        print("모든 테이블이 성공적으로 생성되었습니다.")
    
    def insert_sample_data(self):
        """샘플 데이터 삽입"""
        sample_data_script = """
        -- 샘플 사용자 데이터
        INSERT INTO users (email, password, nickname) VALUES 
        ('admin@example.com', 'hashed_password_1', 'admin');
        INSERT INTO users (email, password, nickname) VALUES 
        ('user1@example.com', 'hashed_password_2', 'user1');
        INSERT INTO users (email, password, nickname) VALUES 
        ('user2@example.com', 'hashed_password_3', 'user2');
        
        -- 샘플 태그 데이터
        INSERT INTO tags (name) VALUES 
        ('Python');
        INSERT INTO tags (name) VALUES 
        ('FastAPI');
        INSERT INTO tags (name) VALUES 
        ('DuckDB');
        INSERT INTO tags (name) VALUES 
        ('Backend');
        INSERT INTO tags (name) VALUES 
        ('Database');
        
        -- 샘플 게시글 데이터
        INSERT INTO posts (user_id, title, content, view_count, like_count) VALUES 
        (1, 'DuckDB와 FastAPI 연동하기', 'DuckDB를 FastAPI와 함께 사용하는 방법을 알아봅시다.', 150, 12);
        INSERT INTO posts (user_id, title, content, view_count, like_count) VALUES 
        (2, 'Python 베스트 프랙티스', 'Python 개발 시 지켜야 할 베스트 프랙티스를 정리했습니다.', 89, 7);
        INSERT INTO posts (user_id, title, content, view_count, like_count) VALUES 
        (3, 'ERD 설계 가이드', '효율적인 ERD 설계 방법론에 대해 알아보겠습니다.', 203, 25);
        
        -- 샘플 게시글-태그 연결 데이터
        INSERT INTO post_tags (post_id, tag_id) VALUES (1, 2);
        INSERT INTO post_tags (post_id, tag_id) VALUES (1, 3);
        INSERT INTO post_tags (post_id, tag_id) VALUES (1, 4);
        INSERT INTO post_tags (post_id, tag_id) VALUES (2, 1);
        INSERT INTO post_tags (post_id, tag_id) VALUES (2, 4);
        INSERT INTO post_tags (post_id, tag_id) VALUES (3, 5);
        
        -- 샘플 댓글 데이터
        INSERT INTO comments (post_id, user_id, parent_comment_id, content) VALUES 
        (1, 2, NULL, '매우 유용한 글이네요! DuckDB 성능이 궁금합니다.');
        INSERT INTO comments (post_id, user_id, parent_comment_id, content) VALUES 
        (1, 3, 1, '저도 궁금해요. 벤치마크 자료가 있나요?');
        INSERT INTO comments (post_id, user_id, parent_comment_id, content) VALUES 
        (1, 1, 1, '곧 성능 테스트 결과를 포스팅하겠습니다.');
        INSERT INTO comments (post_id, user_id, parent_comment_id, content) VALUES 
        (2, 1, NULL, '좋은 정리 감사합니다.');
        INSERT INTO comments (post_id, user_id, parent_comment_id, content) VALUES 
        (3, 2, NULL, 'ERD 설계할 때 항상 참고하겠습니다.');
        
        -- 샘플 좋아요 데이터
        INSERT INTO post_likes (user_id, post_id) VALUES (2, 1);
        INSERT INTO post_likes (user_id, post_id) VALUES (3, 1);
        INSERT INTO post_likes (user_id, post_id) VALUES (1, 2);
        INSERT INTO post_likes (user_id, post_id) VALUES (3, 2);
        INSERT INTO post_likes (user_id, post_id) VALUES (1, 3);
        INSERT INTO post_likes (user_id, post_id) VALUES (2, 3);
        """
        
        self.execute_script(sample_data_script)
        print("샘플 데이터가 성공적으로 삽입되었습니다.")


# 전역 데이터베이스 매니저 인스턴스
db_manager = DuckDBManager()


def init_database():
    """데이터베이스 초기화"""
    print("데이터베이스 초기화 중...")
    db_manager.create_tables()
    db_manager.insert_sample_data()
    print("데이터베이스 초기화 완료!")


def get_db_connection():
    """데이터베이스 연결 반환"""
    return db_manager.get_connection()
