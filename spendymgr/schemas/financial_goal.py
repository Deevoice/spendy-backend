from pydantic import BaseModel
from datetime import datetime


class FinancialGoalBase(BaseModel):
    name: str
    target_amount: float
    deadline: datetime
    monthly_contribution: float


class FinancialGoalCreate(FinancialGoalBase):
    pass


class FinancialGoalResponse(FinancialGoalBase):
    id: int
    user_id: int
    current_amount: float
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
