from typing import List
from fastapi import APIRouter, HTTPException

from app.schemas.item import Item, ItemCreate, ItemResponse

router = APIRouter()

# 임시 데이터 저장소 (실제 프로젝트에서는 데이터베이스 사용)
fake_items_db = [
    {"id": 1, "name": "Sample Item 1", "description": "This is a sample item"},
    {"id": 2, "name": "Sample Item 2", "description": "This is another sample item"},
]


@router.get("/", response_model=List[ItemResponse])
async def get_items():
    """모든 아이템 조회"""
    return fake_items_db


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """특정 아이템 조회"""
    item = next((item for item in fake_items_db if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate):
    """새 아이템 생성"""
    new_item = {
        "id": len(fake_items_db) + 1,
        "name": item.name,
        "description": item.description,
    }
    fake_items_db.append(new_item)
    return new_item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemCreate):
    """아이템 업데이트"""
    existing_item = next((item for item in fake_items_db if item["id"] == item_id), None)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    existing_item.update({
        "name": item.name,
        "description": item.description,
    })
    return existing_item


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    """아이템 삭제"""
    global fake_items_db
    fake_items_db = [item for item in fake_items_db if item["id"] != item_id]
    return {"message": "Item deleted successfully"}
