from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


class TransactionBase(BaseModel):
    amount: float
    type: str
    category: str
    description: Optional[str] = None
    date: datetime


class TransactionCreate(TransactionBase):
    account_id: Optional[int] = None
    from_account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    exchange_rate: Optional[float] = None


class Transaction(TransactionBase):
    id: int
    user_id: int
    account_id: int

    class Config:
        from_attributes = True


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class TransactionStats(BaseModel):
    currencies: Dict[str, dict]  # {currency: {income: float, expense: float}}
    period: str
