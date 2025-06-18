from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all categories for the current user."""
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return categories

@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new category for the current user."""
    db_category = Category(
        user_id=current_user.id,
        name=category.name,
        color=category.color,
        type=category.type
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category 