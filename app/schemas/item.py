from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    """아이템 기본 스키마"""
    name: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    """아이템 생성 스키마"""
    pass


class ItemUpdate(ItemBase):
    """아이템 업데이트 스키마"""
    name: Optional[str] = None


class ItemResponse(ItemBase):
    """아이템 응답 스키마"""
    id: int

    class Config:
        from_attributes = True


class Item(ItemResponse):
    """완전한 아이템 스키마"""
    pass
