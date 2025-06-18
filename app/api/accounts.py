from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[AccountResponse])
def get_accounts(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all accounts for the current user."""
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    return accounts


@router.post("/", response_model=AccountResponse)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new account for the current user."""
    db_account = Account(
        user_id=current_user.id,
        name=account.name,
        balance=account.balance,
        currency=account.currency,
        type=account.type,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account
