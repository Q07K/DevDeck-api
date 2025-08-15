import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_main():
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "DevDeck API is running!"}


def test_health_check():
    """헬스 체크 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_items():
    """아이템 목록 조회 테스트"""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_item():
    """아이템 생성 테스트"""
    item_data = {
        "name": "Test Item",
        "description": "Test Description"
    }
    response = client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 201
    assert response.json()["name"] == item_data["name"]
    assert response.json()["description"] == item_data["description"]


def test_get_item():
    """특정 아이템 조회 테스트"""
    response = client.get("/api/v1/items/1")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "name" in response.json()


def test_get_item_not_found():
    """존재하지 않는 아이템 조회 테스트"""
    response = client.get("/api/v1/items/999")
    assert response.status_code == 404
