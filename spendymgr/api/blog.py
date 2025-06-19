from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile,
    Request,
)
from sqlalchemy.orm import Session
from typing import List
import os

from ..db.session import get_db
from ..models.user import User
from ..models.blog import BlogPost
from ..schemas.blog import BlogPostCreate, BlogPostUpdate, BlogPostResponse
from .deps import get_current_user

router = APIRouter()


@router.post("/", response_model=BlogPostResponse)
async def create_post(
    post: BlogPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = BlogPost(**post.model_dump(), author_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.get("/", response_model=List[BlogPostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 10,
    published_only: bool = True,
    db: Session = Depends(get_db),
):
    query = db.query(BlogPost)
    if published_only:
        query = query.filter(BlogPost.published.is_(True))
    posts = query.order_by(BlogPost.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=BlogPostResponse)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db),
):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=BlogPostResponse)
async def update_post(
    post_id: int,
    post: BlogPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this post"
        )

    update_data = post.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_post, field, value)

    db.commit()
    db.refresh(db_post)
    return db_post


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this post"
        )

    db.delete(db_post)
    db.commit()
    return {"detail": "Post deleted successfully"}


@router.post("/{post_id}/image")
async def upload_post_image(
    post_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None,
):
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.author_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this post"
        )

    os.makedirs("blog_images", exist_ok=True)
    image_filename = f"{post_id}_{image.filename}"
    image_path = f"blog_images/{image_filename}"

    with open(image_path, "wb") as f:
        f.write(await image.read())

    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/blog_images/{image_filename}"

    db_post.image_url = image_url
    db.commit()
    db.refresh(db_post)

    return {"image_url": image_url}
