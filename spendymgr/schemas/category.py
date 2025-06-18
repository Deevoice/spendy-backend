from pydantic import BaseModel
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    color: str
    type: str


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
