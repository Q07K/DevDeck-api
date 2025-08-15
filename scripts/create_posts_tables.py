"""
Posts와 Comments 테이블 생성 스크립트
"""

import os
import sys

import duckdb

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_posts_tables():
    """Create posts and related tables"""
    db_path = "test_devdeck.duckdb"

    # Connect to database
    conn = duckdb.connect(db_path)

    try:
        # Create sequences
        conn.execute("CREATE SEQUENCE IF NOT EXISTS posts_id_seq START 1;")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS comments_id_seq START 1;")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS tags_id_seq START 1;")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS post_tags_id_seq START 1;")
        conn.execute(
            "CREATE SEQUENCE IF NOT EXISTS post_likes_id_seq START 1;"
        )

        # Create tags table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER DEFAULT nextval('tags_id_seq') PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create posts table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
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
            CREATE TABLE IF NOT EXISTS comments (
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
            CREATE TABLE IF NOT EXISTS post_tags (
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
            CREATE TABLE IF NOT EXISTS post_likes (
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
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_post_likes_post_id ON post_likes(post_id);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_post_likes_user_id ON post_likes(user_id);"
        )

        print(
            "✓ Posts, comments, tags, and related tables created successfully"
        )

        # Verify table creation
        tables = conn.execute("SHOW TABLES").fetchall()
        print("Available tables:")
        for table in tables:
            print(f"  - {table[0]}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    create_posts_tables()
