from pydantic import BaseModel
from datetime import datetime


class BudgetBase(BaseModel):
    category: str
    amount: float
    period: str


class BudgetCreate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    spent: float
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
