# DevDeck API

DevDeck 프로젝트를 위한 FastAPI 백엔드 서버입니다.
바이브 코딩을 활용한 간단한 블로그를 만들어보는 강의용 자료입니다.

## 기술 스택

- **FastAPI**: 현대적이고 빠른 Python 웹 프레임워크
- **Pydantic**: 데이터 검증 및 시리얼라이제이션
- **Uvicorn**: ASGI 서버
- **UV**: 빠른 Python 패키지 관리자

## 프로젝트 구조

```
app/
├── __init__.py
├── main.py              # FastAPI 애플리케이션 진입점
├── api/                 # API 라우터들
│   ├── __init__.py
│   ├── api.py          # 메인 API 라우터
│   └── endpoints/      # 개별 엔드포인트들
│       ├── __init__.py
│       └── items.py    # 아이템 관련 엔드포인트
├── core/               # 핵심 설정
│   ├── __init__.py
│   └── config.py       # 애플리케이션 설정
├── models/             # 데이터베이스 모델들 (향후 사용)
│   └── __init__.py
├── schemas/            # Pydantic 스키마들
│   ├── __init__.py
│   └── item.py         # 아이템 스키마
└── services/           # 비즈니스 로직 서비스들
    └── __init__.py

tests/                  # 테스트 파일들
├── __init__.py
└── test_main.py        # 메인 테스트

main.py                 # 애플리케이션 실행 진입점
```

## 설치 및 실행

### 1. 가상환경 활성화
```bash
.\.venv\Scripts\activate  # Windows PowerShell
```

### 2. 의존성이 이미 설치되어 있음
UV를 통해 필요한 패키지들이 자동으로 설치되었습니다.

### 3. 서버 실행
```bash
# 방법 1: 메인 파일을 통한 실행
python main.py

# 방법 2: uvicorn을 직접 사용
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. API 문서 확인
서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 주요 엔드포인트

- `GET /`: 루트 엔드포인트
- `GET /health`: 헬스 체크
- `GET /api/v1/items/`: 모든 아이템 조회
- `POST /api/v1/items/`: 새 아이템 생성
- `GET /api/v1/items/{item_id}`: 특정 아이템 조회
- `PUT /api/v1/items/{item_id}`: 아이템 업데이트
- `DELETE /api/v1/items/{item_id}`: 아이템 삭제

## 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 테스트 실행
pytest --cov=app tests/
```

## 환경 설정

`.env` 파일을 통해 환경 변수를 설정할 수 있습니다:

```env
PROJECT_NAME=DevDeck API
DEBUG=true
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-secret-key
```

## 개발

### 새로운 엔드포인트 추가

1. `app/api/endpoints/`에 새로운 파일 생성
2. `app/schemas/`에 필요한 Pydantic 스키마 정의
3. `app/api/api.py`에 새 라우터 등록

### 데이터베이스 연동 (선택사항)

향후 데이터베이스를 연동할 경우:
1. SQLAlchemy 또는 다른 ORM 설치
2. `app/models/`에 데이터베이스 모델 정의
3. `app/core/database.py`에 데이터베이스 연결 설정
