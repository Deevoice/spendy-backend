from pydantic import BaseModel
from datetime import datetime


class ExchangeRateBase(BaseModel):
    from_currency: str
    to_currency: str
    rate: float


class ExchangeRateCreate(ExchangeRateBase):
    pass


class ExchangeRate(ExchangeRateBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
