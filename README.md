# DevDeck API

DevDeck 프로젝트를 위한 FastAPI 백엔드 서버입니다. DuckDB를 사용하여 블로그 시스템의 완전한 ERD를 구현했습니다.

## 기술 스택

- **백엔드**: FastAPI 0.116+
- **데이터베이스**: DuckDB (파일 기반 SQL 데이터베이스)
- **ORM**: SQLAlchemy 2.0
- **인증**: JWT (python-jose + passlib)
- **테스트**: pytest + pytest-asyncio + pytest-cov
- **개발 도구**: uv (Python 패키지 매니저)
- **API 문서**: Swagger UI, ReDoc

## 데이터베이스 구조
DevDeck 프로젝트를 위한 FastAPI 백엔드 서버입니다. DuckDB를 사용하여 블로그 시스템의 완전한 ERD를 구현했습니다.

## � 기술 스택

- **백엔드**: FastAPI 0.116+
- **데이터베이스**: DuckDB (파일 기반 SQL 데이터베이스)
- **ORM**: SQLAlchemy 2.0
- **인증**: JWT (python-jose + passlib)
- **테스트**: pytest + pytest-asyncio + pytest-cov
- **개발 도구**: uv (Python 패키지 매니저)
- **API 문서**: Swagger UI, ReDoc

## 데이터베이스 구조 (DuckDB)

이 프로젝트는 DuckDB를 사용하여 다음과 같은 ERD를 구현합니다:

### ERD 구성요소

- **Users** - 사용자 정보 (이메일, 닉네임, 비밀번호, JWT 인증)
- **Posts** - 게시글 (제목, 내용, 조회수, 좋아요 수, 소프트 삭제)
- **Comments** - 댓글 시스템 (대댓글 지원, 계층구조)
- **Tags** - 태그 관리
- **Post_Tags** - 게시글-태그 다대다 관계
- **Post_Likes** - 사용자-게시글 좋아요 다대다 관계

### 주요 기능

#### 인증 시스템
- JWT 인증: 토큰 기반 인증 시스템
- 비밀번호 해싱: bcrypt를 사용한 안전한 비밀번호 저장
- 보안 미들웨어: 인증이 필요한 엔드포인트 보호

#### 사용자 관리
- 회원가입/로그인: 이메일 기반 사용자 등록 및 인증
- 프로필 관리: 사용자 정보 조회 및 수정
- 팔로우 시스템: 사용자 간 팔로우/언팔로우

#### 게시글 시스템
- 게시글 CRUD: 작성, 읽기, 수정, 삭제 (소프트 삭제)
- 페이징: 게시글 목록 페이징 및 정렬
- 검색: 제목/내용 기반 게시글 검색
- 조회수: 게시글 조회수 자동 증가
- 인기글: 좋아요 수 기반 인기글 조회

#### 댓글 시스템
- 댓글 CRUD: 댓글 작성, 조회, 수정, 삭제
- 대댓글: 계층구조 댓글 시스템
- 댓글 수: 게시글별 댓글 수 자동 계산

#### 태그 시스템
- 태그 관리: 게시글 태깅 및 태그 관리
- 태그 필터링: 태그별 게시글 필터링
- 태그 목록: 모든 태그 조회

#### 좋아요 시스템
- 좋아요 토글: 게시글 좋아요/취소
- 좋아요 수: 게시글별 좋아요 수 실시간 반영

#### 관리자 기능
- 관리자 대시보드: 전체 통계 및 관리 기능
- 콘텐츠 관리: 게시글/댓글 관리 및 삭제
- 공지사항: 공지사항 작성 및 관리

## 설치 및 실행

### 필수 요구사항

- **Python**: 3.12+
- **uv**: Python 패키지 매니저 (권장) 또는 pip

### 1. 저장소 클론 및 의존성 설치

```bash
# 저장소 클론
git clone https://github.com/Q07K/DevDeck-api.git
cd DevDeck-api

# uv를 사용한 의존성 설치 (권장)
uv sync

# 또는 pip 사용
pip install -r requirements.txt
```

### 2. 데이터베이스 초기화

```bash
# 완전한 테스트 데이터베이스 초기화
uv run python scripts/init_complete_db.py

# 또는 단순 데이터베이스 초기화
uv run python scripts/simple_db_init.py

# 사용자 확인
uv run python scripts/check_users.py
```

### 3. 서버 실행

```bash
# 개발 서버 실행 (uv 사용)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 메인 모듈에서 직접 실행
uv run python main.py

# 또는 pip를 사용하는 경우
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API 접근

- **서버 주소**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/api/v1/docs
- **API 문서 (ReDoc)**: http://localhost:8000/api/v1/redoc
- **헬스 체크**: http://localhost:8000/health

## 테스트

이 프로젝트는 70개의 테스트로 구성된 포괄적인 테스트 슈트를 제공하며, 39%의 코드 커버리지를 달성하고 있습니다.

### 테스트 구조

- `tests/test_auth_api.py` - 인증 API 테스트 (6개): 로그인, 로그아웃, 토큰 검증
- `tests/test_posts_api.py` - 게시글 API 테스트 (9개): CRUD, 좋아요, 페이징
- `tests/test_users_api.py` - 사용자 API 테스트 (11개): 회원가입, 프로필, 팔로우
- `tests/test_blog_api.py` - 블로그 API 테스트 (12개): 태그, 검색, 인기글
- `tests/test_database.py` - 데이터베이스 작업 테스트 (7개): DB 초기화, 서비스 테스트
- `tests/test_api_endpoints.py` - API 엔드포인트 테스트 (10개): 기본 CRUD, 오류 처리
- `tests/test_sqlalchemy_structure.py` - SQLAlchemy ORM 테스트 (9개): 모델, 관계, 트랜잭션
- `tests/test_main.py` - 메인 애플리케이션 테스트 (6개): 루트, 헬스체크

### 빠른 테스트 실행

```bash
# 모든 테스트 실행 (권장)
uv run pytest

# 상세한 출력으로 테스트 실행
uv run pytest -v

# 커버리지 리포트와 함께 실행
uv run pytest --cov=app --cov-report=term-missing

# 편의 스크립트 사용
uv run python run_tests.py all          # 모든 테스트
uv run python run_tests.py auth         # 인증 테스트만
uv run python run_tests.py posts        # 게시글 테스트만
uv run python run_tests.py users        # 사용자 테스트만
uv run python run_tests.py database     # 데이터베이스 테스트만
```

### 상세 테스트 실행 방법

```bash
# 특정 테스트 파일 실행
uv run pytest tests/test_auth_api.py -v

# 특정 테스트 클래스 실행
uv run pytest tests/test_auth_api.py::TestAuthAPI -v

# 특정 테스트 메소드 실행
uv run pytest tests/test_auth_api.py::TestAuthAPI::test_login_success -v

# 마커를 사용한 필터링
uv run pytest -m "not slow"            # 느린 테스트 제외
uv run pytest -m "integration"         # 통합 테스트만
uv run pytest -m "unit"               # 단위 테스트만
uv run pytest -m "api"                # API 테스트만
uv run pytest -m "database"           # 데이터베이스 테스트만
```

### 커버리지 보고서

```bash
# HTML 커버리지 보고서 생성
uv run pytest --cov=app --cov-report=html

# 보고서는 htmlcov/index.html에서 확인 가능
```

### 테스트 픽스처

프로젝트는 다음과 같은 공통 픽스처를 제공합니다:

- `client` - FastAPI 테스트 클라이언트 (모든 API 테스트용)
- `auth_token` - JWT 인증 토큰 (인증이 필요한 테스트용)
- `auth_headers` - 인증 헤더 (Authorization: Bearer {token})
- `test_user_data` - 테스트용 사용자 데이터
- `created_test_user` - 생성된 테스트 사용자 객체
- `test_post_data` - 테스트용 게시글 데이터

### 테스트 마커

프로젝트에서 사용되는 pytest 마커:

- `@pytest.mark.slow` - 실행 시간이 오래 걸리는 테스트
- `@pytest.mark.integration` - 통합 테스트
- `@pytest.mark.unit` - 단위 테스트
- `@pytest.mark.api` - API 테스트
- `@pytest.mark.database` - 데이터베이스 테스트

## API 엔드포인트

### 기본 정보
- **API 베이스 URL**: `/api/v1`
- **인증 방식**: JWT Bearer Token
- **콘텐츠 타입**: `application/json`

### 인증 API
- `POST /api/v1/auth/login` - 사용자 로그인 (이메일/비밀번호)
- `POST /api/v1/auth/logout` - 사용자 로그아웃
- `GET /api/v1/auth/me` - 현재 사용자 정보 조회 (JWT 필요)

### 사용자 관리 API
- `POST /api/v1/blog/users` - 사용자 생성 (회원가입)
- `GET /api/v1/blog/users/{user_id}` - 특정 사용자 조회
- `GET /api/v1/users/me` - 내 프로필 조회 (JWT 필요)
- `PUT /api/v1/users/me` - 내 프로필 수정 (JWT 필요)
- `GET /api/v1/users/{user_id}/posts` - 특정 사용자의 게시글 목록
- `POST /api/v1/users/{user_id}/follow` - 사용자 팔로우 (JWT 필요)
- `DELETE /api/v1/users/{user_id}/follow` - 사용자 언팔로우 (JWT 필요)

### 게시글 관리 API
- `GET /api/v1/blog/posts` - 게시글 목록 조회 (페이징, 태그 필터링 지원)
  - Query params: `page`, `size`, `tag`, `search`
- `GET /api/v1/blog/posts/{post_id}` - 게시글 상세 조회 (조회수 자동 증가)
- `POST /api/v1/blog/posts` - 게시글 생성 (JWT 필요)
- `PUT /api/v1/blog/posts/{post_id}` - 게시글 수정 (JWT 필요, 작성자만)
- `DELETE /api/v1/blog/posts/{post_id}` - 게시글 삭제 (소프트, JWT 필요, 작성자만)
- `GET /api/v1/posts/search` - 게시글 검색 (제목/내용 기반)
- `GET /api/v1/posts/popular` - 인기 게시글 목록 (좋아요 수 기준)
- `GET /api/v1/posts/recent` - 최근 게시글 목록

### 댓글 관리 API
- `GET /api/v1/blog/posts/{post_id}/comments` - 특정 게시글의 댓글 목록 (계층구조)
- `POST /api/v1/blog/comments` - 댓글 생성 (JWT 필요)
  - 대댓글 작성시 `parent_id` 포함
- `PUT /api/v1/comments/{comment_id}` - 댓글 수정 (JWT 필요, 작성자만)
- `DELETE /api/v1/comments/{comment_id}` - 댓글 삭제 (JWT 필요, 작성자만)

### 좋아요 시스템 API
- `POST /api/v1/blog/posts/{post_id}/like` - 게시글 좋아요 토글 (JWT 필요)
  - 이미 좋아요한 경우 취소, 없으면 추가

### 태그 관리 API
- `GET /api/v1/blog/tags` - 모든 태그 목록 조회

### 관리자 API (JWT 필요, 관리자 권한)
- `GET /api/v1/admin/dashboard` - 관리자 대시보드 (통계 정보)
- `GET /api/v1/admin/posts` - 모든 게시글 관리 목록
- `DELETE /api/v1/admin/posts/{post_id}` - 관리자 게시글 삭제 (하드/소프트 선택 가능)
- `DELETE /api/v1/admin/comments/{comment_id}` - 관리자 댓글 삭제
- `POST /api/v1/admin/announcements` - 공지사항 작성
- `GET /api/v1/announcements` - 활성화된 공지사항 조회 (일반 사용자용)

### 시스템 API
- `GET /` - 루트 엔드포인트 (시스템 정보)
- `GET /health` - 헬스 체크 엔드포인트

## API 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 프로젝트 구조

```
DevDeck-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 애플리케이션 팩토리
│   ├── api/                    # API 라우터
│   │   ├── __init__.py
│   │   ├── api.py             # 메인 API 라우터
│   │   └── endpoints/         # API 엔드포인트들
│   │       ├── admin.py       # 관리자 API
│   │       ├── auth.py        # 인증 API
│   │       ├── posts.py       # 게시글 API
│   │       └── users.py       # 사용자 API
│   ├── core/                  # 핵심 설정
│   │   ├── config.py          # 애플리케이션 설정
│   │   ├── database.py        # 데이터베이스 설정
│   │   └── security.py        # JWT 및 보안 설정
│   ├── crud/                  # 데이터베이스 CRUD 작업
│   │   ├── posts.py          # 게시글 관련 DB 작업
│   │   └── users.py          # 사용자 관련 DB 작업
│   ├── models/               # SQLAlchemy 모델들
│   │   ├── comments.py       # 댓글 모델
│   │   ├── posts.py          # 게시글 모델
│   │   ├── post_likes.py     # 좋아요 모델
│   │   ├── post_tags.py      # 게시글-태그 관계 모델
│   │   ├── tags.py           # 태그 모델
│   │   └── users.py          # 사용자 모델
│   ├── schemas/              # Pydantic 스키마들
│   │   ├── auth.py           # 인증 관련 스키마
│   │   ├── database_schemas.py # 기본 데이터베이스 스키마
│   │   ├── posts.py          # 게시글 관련 스키마
│   │   └── users.py          # 사용자 관련 스키마
│   └── services/             # 비즈니스 로직
│       └── database_service.py # 데이터베이스 서비스
├── scripts/                  # 유틸리티 스크립트들
│   ├── check_users.py        # 사용자 확인 스크립트
│   ├── create_test_user.py   # 테스트 사용자 생성
│   ├── init_complete_db.py   # 완전한 DB 초기화
│   └── simple_db_init.py     # 단순 DB 초기화
├── tests/                    # 테스트 파일들 (70개 테스트)
│   ├── conftest.py           # 테스트 설정 및 픽스처
│   ├── test_auth_api.py      # 인증 API 테스트
│   ├── test_blog_api.py      # 블로그 API 테스트
│   ├── test_database.py      # 데이터베이스 테스트
│   ├── test_main.py          # 메인 앱 테스트
│   ├── test_posts_api.py     # 게시글 API 테스트
│   ├── test_sqlalchemy_structure.py # ORM 테스트
│   └── test_users_api.py     # 사용자 API 테스트
├── htmlcov/                  # 커버리지 HTML 보고서
├── main.py                   # 애플리케이션 진입점
├── run_tests.py              # 테스트 실행 편의 스크립트
├── pyproject.toml            # 프로젝트 설정 (uv)
├── pytest.ini               # pytest 설정
├── coverage.xml              # 커버리지 XML 보고서
├── devdeck.duckdb           # 프로덕션 DuckDB 파일
├── test_devdeck.duckdb      # 테스트용 DuckDB 파일
└── README.md                # 프로젝트 문서
```

## 보안 고려사항

- **JWT 토큰**: 만료 시간 30분 (프로덕션에서 `SECRET_KEY` 변경 필수)
- **비밀번호 해싱**: bcrypt를 사용한 안전한 해싱
- **CORS 설정**: 개발 환경용으로 설정 (프로덕션에서 조정 필요)
- **입력 검증**: Pydantic을 통한 자동 데이터 검증
- **SQL 인젝션 방지**: SQLAlchemy ORM 사용으로 자동 방지

## 배포 고려사항

### 환경 변수 설정
```bash
# .env 파일 생성
PROJECT_NAME="DevDeck API Production"
DEBUG=false
SECRET_KEY="your-super-secret-key-here"
DATABASE_URL="duckdb:///./prod_devdeck.duckdb"
ALLOWED_ORIGINS=["https://your-frontend-domain.com"]
```

### 프로덕션 실행
```bash
# 프로덕션 모드로 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참고하세요.

## 연락처

- **프로젝트 링크**: [https://github.com/Q07K/DevDeck-api](https://github.com/Q07K/DevDeck-api)
- **이슈 및 버그 리포트**: [GitHub Issues](https://github.com/Q07K/DevDeck-api/issues)
