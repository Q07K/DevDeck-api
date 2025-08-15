# DevDeck API

DevDeck 프로젝트를 위한 FastAPI 백엔드 서버입니다. DuckDB를 사용하여 블로그 시스템의 완전한 ERD를 구현했습니다.

## 🗄️ 데이터베이스 구조 (DuckDB)

이 프로젝트는 DuckDB를 사용하여 다음과 같은 ERD를 구현합니다:

### 📊 ERD 구성요소

- **Users** - 사용자 정보 (이메일, 닉네임, 비밀번호)
- **Posts** - 게시글 (제목, 내용, 조회수, 좋아요 수, 소프트 삭제)
- **Comments** - 댓글 시스템 (대댓글 지원)
- **Tags** - 태그 관리
- **Post_Tags** - 게시글-태그 다대다 관계
- **Post_Likes** - 사용자-게시글 좋아요 다대다 관계

### 🔧 주요 기능

- ✅ **사용자 관리**: 회원가입, 로그인, 프로필 관리
- ✅ **게시글 CRUD**: 작성, 읽기, 수정, 삭제 (소프트 삭제)
- ✅ **댓글 시스템**: 댓글 및 대댓글 지원
- ✅ **태그 시스템**: 게시글 태깅 및 태그별 필터링
- ✅ **좋아요 기능**: 게시글 좋아요/취소
- ✅ **페이징**: 게시글 목록 페이징 지원
- ✅ **조회수**: 게시글 조회수 자동 증가

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
# Python 환경 설정 (uv 사용)
uv sync

# 또는 pip 사용
pip install fastapi uvicorn duckdb sqlalchemy alembic email-validator
```

### 2. 데이터베이스 초기화

```bash
# 데이터베이스 테스트 및 초기화
python scripts/test_database.py
```

### 3. 서버 실행

```bash
# 개발 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 또는 app.main에서 실행
uvicorn app.main:app --reload
```

### 4. 테스트 실행

```bash
# 모든 테스트 실행
uv run pytest tests/ -v

# 특정 테스트 파일 실행
uv run pytest tests/test_auth_api.py -v

# 커버리지 포함 테스트
uv run pytest tests/ --cov=app --cov-report=term-missing

# 편의 스크립트 사용
python run_tests.py auth        # 인증 API 테스트
python run_tests.py posts       # 게시글 API 테스트
python run_tests.py users       # 사용자 API 테스트
python run_tests.py database    # 데이터베이스 테스트
python run_tests.py all -v -c   # 모든 테스트 (상세 출력, 커버리지 포함)
```

### 5. API 테스트

```bash
# API 엔드포인트 테스트 (서버 실행 후)
pip install requests  # requests 설치 후
python scripts/test_api.py  # 주의: scripts에서 tests로 이관됨
```

## 🧪 테스트

이 프로젝트는 pytest를 사용하여 포괄적인 테스트 슈트를 제공합니다.

### 테스트 구조

- `tests/test_auth_api.py` - 인증 API 테스트
- `tests/test_posts_api.py` - 게시글 API 테스트  
- `tests/test_users_api.py` - 사용자 API 테스트
- `tests/test_blog_api.py` - 블로그 API 테스트
- `tests/test_database.py` - 데이터베이스 작업 테스트
- `tests/test_api_endpoints.py` - 엔드포인트 테스트
- `tests/test_sqlalchemy_structure.py` - SQLAlchemy ORM 테스트
- `tests/test_main.py` - 메인 애플리케이션 테스트

### 테스트 실행 방법

```bash
# 모든 테스트 실행
uv run pytest

# 상세한 출력으로 테스트 실행
uv run pytest -v

# 커버리지 리포트와 함께 실행
uv run pytest --cov=app --cov-report=term-missing

# 특정 테스트 파일만 실행
uv run pytest tests/test_auth_api.py

# 특정 테스트 클래스 실행
uv run pytest tests/test_auth_api.py::TestAuthAPI

# 특정 테스트 메소드 실행
uv run pytest tests/test_auth_api.py::TestAuthAPI::test_login_success

# 마커를 사용한 필터링
uv run pytest -m "not slow"        # 느린 테스트 제외
uv run pytest -m "integration"     # 통합 테스트만
uv run pytest -m "unit"           # 단위 테스트만
```

### 편의 스크립트 사용

```bash
# 테스트 실행 스크립트
python run_tests.py auth        # 인증 테스트
python run_tests.py posts       # 게시글 테스트
python run_tests.py users       # 사용자 테스트
python run_tests.py database    # 데이터베이스 테스트
python run_tests.py all -v -c   # 모든 테스트 (상세 출력, 커버리지)

# 특정 마커로 필터링
python run_tests.py all -m "not slow"  # 느린 테스트 제외
```

### 테스트 픽스처

프로젝트는 다음과 같은 공통 픽스처를 제공합니다:

- `client` - FastAPI 테스트 클라이언트
- `auth_token` - 인증 토큰
- `auth_headers` - 인증 헤더
- `test_user_data` - 테스트용 사용자 데이터
- `created_test_user` - 생성된 테스트 사용자
- `test_post_data` - 테스트용 게시글 데이터

## 📡 API 엔드포인트

### 사용자 관리
- `POST /api/v1/blog/users` - 사용자 생성
- `GET /api/v1/blog/users/{user_id}` - 사용자 조회

### 게시글 관리
- `GET /api/v1/blog/posts` - 게시글 목록 (페이징, 태그 필터링)
- `GET /api/v1/blog/posts/{post_id}` - 게시글 상세 조회
- `POST /api/v1/blog/posts` - 게시글 생성
- `PUT /api/v1/blog/posts/{post_id}` - 게시글 수정
- `DELETE /api/v1/blog/posts/{post_id}` - 게시글 삭제 (소프트)

### 댓글 관리
- `GET /api/v1/blog/posts/{post_id}/comments` - 댓글 목록 (계층구조)
- `POST /api/v1/blog/comments` - 댓글 생성

### 상호작용
- `POST /api/v1/blog/posts/{post_id}/like` - 좋아요 토글

### 태그 관리
- `GET /api/v1/blog/tags` - 모든 태그 조회

## 📋 API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
