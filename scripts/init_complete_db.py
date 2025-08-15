"""
완전한 데이터베이스 초기화 스크립트 (사용자, 글, 댓글 테이블 포함)
"""

import os
import sys

import duckdb

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash


def create_complete_database():
    """Create complete database with all tables and test data"""
    db_path = "test_devdeck.duckdb"

    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")

    # Connect to new database
    conn = duckdb.connect(db_path)

    try:
        # Create sequences
        conn.execute("CREATE SEQUENCE users_id_seq START 1;")
        conn.execute("CREATE SEQUENCE posts_id_seq START 1;")
        conn.execute("CREATE SEQUENCE comments_id_seq START 1;")
        conn.execute("CREATE SEQUENCE tags_id_seq START 1;")
        conn.execute("CREATE SEQUENCE post_tags_id_seq START 1;")
        conn.execute("CREATE SEQUENCE post_likes_id_seq START 1;")

        # Create users table
        conn.execute(
            """
            CREATE TABLE users (
                id INTEGER DEFAULT nextval('users_id_seq') PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                nickname VARCHAR(50) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create tags table
        conn.execute(
            """
            CREATE TABLE tags (
                id INTEGER DEFAULT nextval('tags_id_seq') PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create posts table
        conn.execute(
            """
            CREATE TABLE posts (
                id INTEGER DEFAULT nextval('posts_id_seq') PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """
        )

        # Create comments table
        conn.execute(
            """
            CREATE TABLE comments (
                id INTEGER DEFAULT nextval('comments_id_seq') PRIMARY KEY,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                parent_comment_id INTEGER,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (parent_comment_id) REFERENCES comments(id)
            )
        """
        )

        # Create post_tags table
        conn.execute(
            """
            CREATE TABLE post_tags (
                id INTEGER DEFAULT nextval('post_tags_id_seq') PRIMARY KEY,
                post_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id),
                UNIQUE(post_id, tag_id)
            )
        """
        )

        # Create post_likes table
        conn.execute(
            """
            CREATE TABLE post_likes (
                id INTEGER DEFAULT nextval('post_likes_id_seq') PRIMARY KEY,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(post_id, user_id)
            )
        """
        )

        # Create indexes
        conn.execute("CREATE INDEX idx_posts_user_id ON posts(user_id);")
        conn.execute("CREATE INDEX idx_posts_created_at ON posts(created_at);")
        conn.execute("CREATE INDEX idx_comments_post_id ON comments(post_id);")
        conn.execute("CREATE INDEX idx_comments_user_id ON comments(user_id);")

        print("✓ All tables created successfully")

        # Insert test users
        test_password = get_password_hash("password123")
        admin_password = get_password_hash("admin123")

        conn.execute(
            """
            INSERT INTO users (email, password, nickname)
            VALUES (?, ?, ?)
        """,
            ("user@example.com", test_password, "testuser"),
        )

        conn.execute(
            """
            INSERT INTO users (email, password, nickname)
            VALUES (?, ?, ?)
        """,
            ("admin@example.com", admin_password, "admin"),
        )

        # Insert test tags
        conn.execute("INSERT INTO tags (name) VALUES ('Python')")
        conn.execute("INSERT INTO tags (name) VALUES ('FastAPI')")
        conn.execute("INSERT INTO tags (name) VALUES ('React')")
        conn.execute("INSERT INTO tags (name) VALUES ('TypeScript')")

        # Insert test posts
        conn.execute(
            """
            INSERT INTO posts (user_id, title, content, view_count, like_count)
            VALUES (1, 'FastAPI 시작하기', 'FastAPI는 현대적이고 빠른 웹 프레임워크입니다. Python 3.7+의 타입 힌트를 기반으로 API를 구축할 수 있습니다.', 10, 5)
        """
        )

        conn.execute(
            """
            INSERT INTO posts (user_id, title, content, view_count, like_count)
            VALUES (1, 'React와 TypeScript', 'React와 TypeScript를 함께 사용하면 더욱 안전하고 유지보수하기 쉬운 프론트엔드 애플리케이션을 만들 수 있습니다.', 25, 12)
        """
        )

        # Link posts with tags
        conn.execute(
            "INSERT INTO post_tags (post_id, tag_id) VALUES (1, 1)"
        )  # Python
        conn.execute(
            "INSERT INTO post_tags (post_id, tag_id) VALUES (1, 2)"
        )  # FastAPI
        conn.execute(
            "INSERT INTO post_tags (post_id, tag_id) VALUES (2, 3)"
        )  # React
        conn.execute(
            "INSERT INTO post_tags (post_id, tag_id) VALUES (2, 4)"
        )  # TypeScript

        # Insert test comments
        conn.execute(
            """
            INSERT INTO comments (post_id, user_id, content)
            VALUES (1, 2, '좋은 글 감사합니다! FastAPI 정말 좋네요.')
        """
        )

        conn.execute(
            """
            INSERT INTO comments (post_id, user_id, parent_comment_id, content)
            VALUES (1, 1, 1, '감사합니다! 더 자세한 내용은 다음 글에서 다루겠습니다.')
        """
        )

        print("✓ Test data inserted successfully")

        # Verify data
        users = conn.execute("SELECT email, nickname FROM users").fetchall()
        posts = conn.execute(
            "SELECT title, view_count, like_count FROM posts"
        ).fetchall()
        comments = conn.execute(
            "SELECT content, parent_comment_id FROM comments"
        ).fetchall()

        print("\nDatabase verification:")
        print(f"Users: {len(users)}")
        for user in users:
            print(f"  - {user[0]} ({user[1]})")

        print(f"Posts: {len(posts)}")
        for post in posts:
            print(f"  - {post[0]} (views: {post[1]}, likes: {post[2]})")

        print(f"Comments: {len(comments)}")
        for comment in comments:
            parent = f" (reply to {comment[1]})" if comment[1] else ""
            print(f"  - {comment[0][:50]}...{parent}")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    create_complete_database()
