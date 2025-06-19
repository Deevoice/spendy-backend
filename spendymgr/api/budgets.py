from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from spendymgr.database import get_db
from spendymgr.models.budget import Budget
from spendymgr.schemas.budget import BudgetCreate, BudgetResponse
from spendymgr.api.deps import get_current_user
from spendymgr.models.user import User

router = APIRouter()


@router.get("/", response_model=List[BudgetResponse])
def get_budgets(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all budgets for the current user."""
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    return budgets


@router.post("/", response_model=BudgetResponse)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new budget for the current user."""
    db_budget = Budget(
        user_id=current_user.id,
        category=budget.category,
        amount=budget.amount,
        period=budget.period,
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.patch("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a budget."""
    db_budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )

    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    for key, value in budget.dict().items():
        setattr(db_budget, key, value)

    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a budget."""
    db_budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )

    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    db.delete(db_budget)
    db.commit()
    return {"message": "Budget deleted successfully"}
