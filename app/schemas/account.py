from pydantic import BaseModel
from datetime import datetime


class AccountBase(BaseModel):
    name: str
    balance: float
    currency: str
    type: str


class AccountCreate(AccountBase):
    pass


class AccountResponse(AccountBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
