from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from ..database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    from_currency = Column(String, index=True)
    to_currency = Column(String, index=True)
    rate = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
