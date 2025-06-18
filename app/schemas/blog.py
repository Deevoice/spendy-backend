from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BlogPostBase(BaseModel):
    title: str
    content: str
    slug: str
    published: bool = False
    image_url: Optional[str] = None


class BlogPostCreate(BlogPostBase):
    pass


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    published: Optional[bool] = None
    image_url: Optional[str] = None


class BlogPostResponse(BlogPostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
