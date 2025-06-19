from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from spendymgr.database import get_db
from spendymgr.models.financial_goal import FinancialGoal
from spendymgr.schemas.financial_goal import FinancialGoalCreate, FinancialGoalResponse
from spendymgr.api.deps import get_current_user
from spendymgr.models.user import User

router = APIRouter()


@router.get("/", response_model=List[FinancialGoalResponse])
def get_financial_goals(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all financial goals for the current user."""
    goals = (
        db.query(FinancialGoal).filter(FinancialGoal.user_id == current_user.id).all()
    )
    return goals


@router.post("/", response_model=FinancialGoalResponse)
def create_financial_goal(
    goal: FinancialGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new financial goal for the current user."""
    db_goal = FinancialGoal(
        user_id=current_user.id,
        name=goal.name,
        target_amount=goal.target_amount,
        deadline=goal.deadline,
        monthly_contribution=goal.monthly_contribution,
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.patch("/{goal_id}", response_model=FinancialGoalResponse)
def update_financial_goal(
    goal_id: int,
    goal: FinancialGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a financial goal."""
    db_goal = (
        db.query(FinancialGoal)
        .filter(FinancialGoal.id == goal_id, FinancialGoal.user_id == current_user.id)
        .first()
    )

    if not db_goal:
        raise HTTPException(status_code=404, detail="Financial goal not found")

    for key, value in goal.dict().items():
        setattr(db_goal, key, value)

    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.delete("/{goal_id}")
def delete_financial_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a financial goal."""
    db_goal = (
        db.query(FinancialGoal)
        .filter(FinancialGoal.id == goal_id, FinancialGoal.user_id == current_user.id)
        .first()
    )

    if not db_goal:
        raise HTTPException(status_code=404, detail="Financial goal not found")

    db.delete(db_goal)
    db.commit()
    return {"message": "Financial goal deleted successfully"}
