"""
DuckDB 데이터베이스 초기화 및 테스트 스크립트

이 스크립트는:
1. DuckDB 데이터베이스를 초기화합니다.
2. ERD에 정의된 모든 테이블을 생성합니다.
3. 샘플 데이터를 삽입합니다.
4. 기본적인 CRUD 작업을 테스트합니다.
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db_manager, init_database
from app.services.database_service import UserService, PostService, CommentService, TagService
from app.schemas.database_schemas import UserCreate, PostCreate, CommentCreate


def test_database_operations():
    """데이터베이스 작업 테스트"""
    print("=== DuckDB 데이터베이스 테스트 시작 ===\n")
    
    try:
        # 1. 데이터베이스 초기화
        print("1. 데이터베이스 초기화 중...")
        init_database()
        print("✓ 데이터베이스 초기화 완료\n")
        
        # 2. 사용자 조회 테스트
        print("2. 사용자 데이터 조회 테스트...")
        user = UserService.get_user_by_id(1)
        if user:
            print(f"✓ 사용자 조회 성공: {user['nickname']} ({user['email']})")
        else:
            print("✗ 사용자 조회 실패")
        print()
        
        # 3. 게시글 목록 조회 테스트
        print("3. 게시글 목록 조회 테스트...")
        posts = PostService.get_posts_list(page=1, per_page=5)
        print(f"✓ 게시글 목록 조회 성공: 총 {posts['total']}개 게시글")
        for post in posts['items']:
            print(f"  - {post['title']} (조회수: {post['view_count']}, 좋아요: {post['like_count']})")
        print()
        
        # 4. 게시글 상세 조회 테스트
        print("4. 게시글 상세 조회 테스트...")
        post_detail = PostService.get_post_by_id(1, increment_view=True)
        if post_detail:
            print(f"✓ 게시글 상세 조회 성공: '{post_detail['title']}'")
            print(f"  작성자: {post_detail['author']['nickname']}")
            print(f"  태그: {', '.join(post_detail['tags'])}")
            print(f"  조회수: {post_detail['view_count']}")
        else:
            print("✗ 게시글 상세 조회 실패")
        print()
        
        # 5. 댓글 조회 테스트
        print("5. 댓글 조회 테스트...")
        comments = CommentService.get_comments_by_post_id(1)
        print(f"✓ 댓글 조회 성공: 총 {len(comments)}개 최상위 댓글")
        for comment in comments:
            print(f"  - {comment['author_nickname']}: {comment['content'][:50]}...")
            if comment['replies']:
                for reply in comment['replies']:
                    print(f"    └ {reply['author_nickname']}: {reply['content'][:50]}...")
        print()
        
        # 6. 태그 조회 테스트
        print("6. 태그 조회 테스트...")
        tags = TagService.get_all_tags()
        print(f"✓ 태그 조회 성공: 총 {len(tags)}개 태그")
        for tag in tags:
            print(f"  - {tag['name']} ({tag['post_count']}개 게시글)")
        print()
        
        # 7. 새 게시글 작성 테스트
        print("7. 새 게시글 작성 테스트...")
        new_post_data = PostCreate(
            title="DuckDB 테스트 게시글",
            content="이것은 DuckDB를 테스트하기 위한 게시글입니다.",
            tag_names=["DuckDB", "테스트", "새로운태그"]
        )
        new_post = PostService.create_post(1, new_post_data)
        print(f"✓ 새 게시글 작성 성공: ID {new_post['id']}, 제목: '{new_post['title']}'")
        print()
        
        # 8. 새 댓글 작성 테스트
        print("8. 새 댓글 작성 테스트...")
        new_comment_data = CommentCreate(
            post_id=new_post['id'],
            content="DuckDB 테스트 댓글입니다."
        )
        new_comment = CommentService.create_comment(2, new_comment_data)
        print(f"✓ 새 댓글 작성 성공: ID {new_comment['id']}")
        print()
        
        # 9. 데이터베이스 통계 조회
        print("9. 데이터베이스 통계...")
        conn = db_manager.get_connection()
        
        # 테이블별 레코드 수 조회
        tables = ['users', 'posts', 'comments', 'tags', 'post_tags', 'post_likes']
        print("테이블별 레코드 수:")
        for table in tables:
            count_result = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            print(f"  - {table}: {count_result[0]}개")
        
        print("\n=== DuckDB 데이터베이스 테스트 완료 ===")
        print("모든 테스트가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"✗ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 데이터베이스 연결 종료
        db_manager.close_connection()


def show_database_schema():
    """데이터베이스 스키마 정보 출력"""
    print("=== DuckDB 스키마 정보 ===\n")
    
    conn = db_manager.get_connection()
    
    # 모든 테이블 목록 조회
    tables_query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'main' 
    ORDER BY table_name
    """
    
    tables = conn.execute(tables_query).fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"📋 테이블: {table_name}")
        
        # 테이블 구조 조회
        columns_query = f"""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
        """
        
        columns = conn.execute(columns_query).fetchall()
        
        for column in columns:
            nullable = "NULL" if column[2] == "YES" else "NOT NULL"
            default = f" DEFAULT {column[3]}" if column[3] else ""
            print(f"  • {column[0]}: {column[1]} {nullable}{default}")
        
        print()


if __name__ == "__main__":
    print("DuckDB 데이터베이스 설정 및 테스트")
    print("=" * 50)
    
    choice = input("\n실행할 작업을 선택하세요:\n1. 데이터베이스 테스트 실행\n2. 스키마 정보 출력\n3. 둘 다 실행\n선택 (1/2/3): ")
    
    if choice == "1":
        test_database_operations()
    elif choice == "2":
        show_database_schema()
    elif choice == "3":
        test_database_operations()
        print("\n" + "="*50 + "\n")
        show_database_schema()
    else:
        print("잘못된 선택입니다.")
