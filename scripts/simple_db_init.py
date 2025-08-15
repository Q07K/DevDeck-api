"""
Simple database initialization and user creation script
"""

import os
import sys

import duckdb

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import get_password_hash


def create_simple_database():
    """Create database with simple SQL"""
    db_path = "test_devdeck.duckdb"

    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)

    # Connect to new database
    conn = duckdb.connect(db_path)

    try:
        # Create users table
        conn.execute(
            """
            CREATE SEQUENCE users_id_seq START 1;
        """
        )

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

        # Create test user
        hashed_password = get_password_hash("password123")
        conn.execute(
            """
            INSERT INTO users (email, password, nickname)
            VALUES (?, ?, ?)
        """,
            ("user@example.com", hashed_password, "testuser"),
        )

        print("✓ Database and test user created successfully")

        # Verify user creation
        result = conn.execute("SELECT email, nickname FROM users").fetchall()
        for row in result:
            print(f"User: {row[0]} (nickname: {row[1]})")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    create_simple_database()
