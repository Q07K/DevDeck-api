from typing import Generator, Optional

import duckdb
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models import Base


class DuckDBManager:
    """DuckDB 데이터베이스 매니저 (Raw SQL용)"""

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
            statements = [
                stmt.strip() for stmt in script.split(";") if stmt.strip()
            ]
            for statement in statements:
                if statement:
                    conn.execute(statement)
        except Exception as e:
            print(f"Script execution error: {e}")
            raise


class SQLAlchemyManager:
    """SQLAlchemy ORM 데이터베이스 매니저"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DUCKDB_FILE
        # DuckDB 엔진 URL 생성
        self.database_url = f"duckdb:///{self.db_path}"
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self):
        """SQLAlchemy 모델을 기반으로 테이블 생성"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """모든 테이블 삭제"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """SQLAlchemy 세션 반환"""
        return self.SessionLocal()

    def get_db(self) -> Generator[Session, None, None]:
        """FastAPI 의존성용 데이터베이스 세션 제너레이터"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# 전역 매니저 인스턴스들
duckdb_manager = DuckDBManager()
sqlalchemy_manager = SQLAlchemyManager()

# 편의를 위한 별칭
get_db = sqlalchemy_manager.get_db


def init_database():
    """데이터베이스 초기화"""
    try:
        # SQLAlchemy로 테이블 생성
        sqlalchemy_manager.create_tables()
        print("✓ SQLAlchemy 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {str(e)}")
