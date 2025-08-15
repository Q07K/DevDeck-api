"""
Pytest configuration and shared fixtures

This module contains shared fixtures and configuration for all tests.
"""

import os
import sys
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

# 프로젝트 루트 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_database

# Import your FastAPI app
from app.main import app


@pytest.fixture(scope="session")
def client():
    """FastAPI 테스트 클라이언트 픽스처"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """테스트 데이터베이스 설정"""
    try:
        # 테스트용 데이터베이스 초기화
        init_database()
        yield
    except Exception as e:
        print(f"Database setup failed: {e}")
        # 데이터베이스 설정에 실패해도 테스트는 계속 진행
        yield


@pytest.fixture
def auth_token(client):
    """인증 토큰을 제공하는 전역 픽스처"""
    login_data = {"email": "user@example.com", "password": "password123"}

    try:
        response = client.post("/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json().get("accessToken")
    except Exception:
        pass

    return None


@pytest.fixture
def auth_headers(auth_token):
    """인증 헤더를 제공하는 전역 픽스처"""
    if auth_token:
        return {"Authorization": f"Bearer {auth_token}"}
    return {}


@pytest.fixture
def test_user_data():
    """테스트용 사용자 데이터 픽스처"""
    timestamp = datetime.now().strftime("%H%M%S%f")
    return {
        "email": f"test_user_{timestamp}@example.com",
        "password": "testpassword123",
        "nickname": f"test_user_{timestamp}",
    }


@pytest.fixture
def created_test_user(client, test_user_data):
    """테스트용 사용자를 생성하는 픽스처"""
    try:
        response = client.post("/api/v1/users/signup", json=test_user_data)
        if response.status_code == 201:
            return response.json()
    except Exception:
        pass

    return None


@pytest.fixture
def test_post_data():
    """테스트용 게시글 데이터 픽스처"""
    timestamp = datetime.now().strftime("%H%M%S")
    return {
        "title": f"Test Post {timestamp}",
        "content": "This is a test post for pytest testing.",
        "tags": ["test", "pytest", "api"],
    }


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """각 테스트 후 정리 작업 (필요한 경우)"""
    yield
    # 테스트 후 정리 작업이 필요한 경우 여기에 구현
    # 예: 임시 생성된 데이터 삭제 등


def pytest_configure(config):
    """Pytest 설정"""
    # 커스텀 마커 등록
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "api: marks tests as API tests")
    config.addinivalue_line(
        "markers", "database: marks tests as database tests"
    )


def pytest_collection_modifyitems(config, items):
    """테스트 아이템 수정"""
    # 느린 테스트에 대한 마커 자동 적용
    for item in items:
        # 데이터베이스 관련 테스트는 slow 마커 추가
        if "database" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)

        # API 테스트는 integration 마커 추가
        if "api" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def event_loop():
    """asyncio 이벤트 루프 픽스처 (비동기 테스트용)"""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# 테스트 실행 전후 훅
def pytest_sessionstart(session):
    """테스트 세션 시작 시 실행"""
    print("\n🚀 Starting pytest test session...")


def pytest_sessionfinish(session, exitstatus):
    """테스트 세션 종료 시 실행"""
    if exitstatus == 0:
        print("\n✅ All tests passed successfully!")
    else:
        print(f"\n❌ Tests finished with exit status: {exitstatus}")


# 테스트 실패 시 추가 정보 제공
def pytest_runtest_makereport(item, call):
    """테스트 실행 보고서 생성"""
    if call.when == "call" and call.excinfo is not None:
        # 테스트 실패 시 추가 디버깅 정보 수집
        if hasattr(item, "funcargs"):
            # 픽스처 정보 등을 로그에 포함
            pass
