from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import requests
from datetime import datetime, timedelta
from ..database import get_db
from ..models.exchange_rate import ExchangeRate
from ..schemas.exchange_rate import ExchangeRateCreate
from ..auth import get_current_user

router = APIRouter()

EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/"
CACHE_DURATION = timedelta(hours=1)


@router.get("/exchange-rate")
async def get_exchange_rate(
    from_currency: str,
    to_currency: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Проверяем кэш в базе данных
    cached_rate = (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.from_currency == from_currency,
            ExchangeRate.to_currency == to_currency,
            ExchangeRate.created_at >= datetime.utcnow() - CACHE_DURATION,
        )
        .first()
    )

    if cached_rate:
        return {"rate": cached_rate.rate}

    try:
        # Получаем курс через API
        response = requests.get(f"{EXCHANGE_RATE_API_URL}{from_currency}")
        response.raise_for_status()
        data = response.json()

        if to_currency not in data["rates"]:
            raise HTTPException(status_code=400, detail="Unsupported currency pair")

        rate = data["rates"][to_currency]

        # Сохраняем в кэш
        exchange_rate = ExchangeRate(
            from_currency=from_currency, to_currency=to_currency, rate=rate
        )
        db.add(exchange_rate)
        db.commit()

        return {"rate": rate}

    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail="Failed to fetch exchange rate")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
