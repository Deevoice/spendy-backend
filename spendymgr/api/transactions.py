from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from spendymgr.database import get_db
from spendymgr.models.transaction import Transaction
from spendymgr.models.account import Account
from spendymgr.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionStats,
)
from spendymgr.models.user import User
from .deps import get_current_user
from pydantic import BaseModel

router = APIRouter()


class CurrencyBalance(BaseModel):
    currency: str
    balance: float
    income: float
    expense: float


def calculate_account_balance(account_id: int, db: Session) -> float:
    """Calculate account balance based on initial balance and transactions."""
    # Получаем счет
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return 0.0

    # Получаем все транзакции для счета
    transactions = (
        db.query(Transaction).filter(Transaction.account_id == account_id).all()
    )

    # Начинаем с начального баланса
    balance = account.balance

    # Добавляем/вычитаем транзакции
    for transaction in transactions:
        if transaction.type == "income":
            balance += transaction.amount
        else:  # expense
            balance -= transaction.amount

    return balance


def calculate_balances_by_currency(
    user_id: int, db: Session
) -> Dict[str, CurrencyBalance]:
    """Calculate balances for each currency."""
    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    balances = {}

    for account in accounts:
        if account.currency not in balances:
            balances[account.currency] = CurrencyBalance(
                currency=account.currency, balance=0.0, income=0.0, expense=0.0
            )

        transactions = (
            db.query(Transaction).filter(Transaction.account_id == account.id).all()
        )

        for transaction in transactions:
            if transaction.type == "income":
                balances[account.currency].income += float(transaction.amount)
                balances[account.currency].balance += float(transaction.amount)
            elif transaction.type == "expense":
                balances[account.currency].expense += float(transaction.amount)
                balances[account.currency].balance -= float(transaction.amount)

    return balances


def get_date_range(period: str) -> tuple[datetime, datetime]:
    """Get start and end dates for the specified period."""
    end_date = datetime.now()
    if period == "day":
        start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = end_date - timedelta(days=7)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "year":
        start_date = end_date - timedelta(days=365)
    else:
        raise HTTPException(status_code=400, detail="Invalid period")
    return start_date, end_date


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    period: str = Query("month", description="Time period: day, week, month, year"),
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get transactions for the current user within the specified period."""
    start_date, end_date = get_date_range(period)

    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    )

    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    return query.order_by(Transaction.date.desc()).all()


@router.get("/stats", response_model=TransactionStats)
def get_transaction_stats(
    period: str = Query("month", description="Time period: day, week, month, year"),
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get transaction statistics for the current user within the specified period."""
    start_date, end_date = get_date_range(period)

    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date,
    )

    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    transactions = query.all()

    income = sum(t.amount for t in transactions if t.type == "income")
    expense = sum(t.amount for t in transactions if t.type == "expense")

    return TransactionStats(income=income, expense=expense, period=period)


@router.get("/balances", response_model=Dict[str, CurrencyBalance])
def get_balances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get balances for all currencies."""
    return calculate_balances_by_currency(current_user.id, db)


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new transaction for the current user and update account balance."""
    # Получаем счет
    account = (
        db.query(Account)
        .filter(
            Account.id == transaction.account_id, Account.user_id == current_user.id
        )
        .first()
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Создаем транзакцию
    db_transaction = Transaction(
        user_id=current_user.id,
        account_id=transaction.account_id,
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category,
        description=transaction.description,
        date=transaction.date,
    )

    try:
        # Добавляем транзакцию
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)

        # Пересчитываем баланс с учетом всех транзакций
        new_balance = calculate_account_balance(transaction.account_id, db)
        account.balance = new_balance
        db.commit()
        db.refresh(account)

        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an existing transaction and recalculate account balance."""
    # Получаем существующую транзакцию
    db_transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id, Transaction.user_id == current_user.id
        )
        .first()
    )

    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Получаем счет
    account = (
        db.query(Account)
        .filter(
            Account.id == transaction.account_id, Account.user_id == current_user.id
        )
        .first()
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        # Обновляем транзакцию
        db_transaction.account_id = transaction.account_id
        db_transaction.amount = transaction.amount
        db_transaction.type = transaction.type
        db_transaction.category = transaction.category
        db_transaction.description = transaction.description
        db_transaction.date = transaction.date

        db.commit()
        db.refresh(db_transaction)

        # Пересчитываем баланс с учетом всех транзакций
        new_balance = calculate_account_balance(transaction.account_id, db)
        account.balance = new_balance
        db.commit()
        db.refresh(account)

        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a transaction and revert account balance."""
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id, Transaction.user_id == current_user.id
        )
        .first()
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Получаем счет
    account = (
        db.query(Account)
        .filter(
            Account.id == transaction.account_id, Account.user_id == current_user.id
        )
        .first()
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        # Удаляем транзакцию
        db.delete(transaction)
        db.commit()

        # Пересчитываем баланс с учетом всех оставшихся транзакций
        new_balance = calculate_account_balance(transaction.account_id, db)
        account.balance = new_balance
        db.commit()
        db.refresh(account)

        return {"message": "Transaction deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transfer", response_model=Dict[str, str])
async def create_transfer(
    transfer: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a transfer between accounts."""
    # Проверяем существование счетов
    from_account = (
        db.query(Account)
        .filter(
            Account.id == transfer.from_account_id, Account.user_id == current_user.id
        )
        .first()
    )

    to_account = (
        db.query(Account)
        .filter(
            Account.id == transfer.to_account_id, Account.user_id == current_user.id
        )
        .first()
    )

    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Проверяем достаточность средств
    if from_account.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    try:
        # Создаем транзакцию списания
        from_transaction = Transaction(
            user_id=current_user.id,
            account_id=from_account.id,
            amount=transfer.amount,
            type="expense",
            category="Transfer",
            description=transfer.description or f"Transfer to {to_account.name}",
            date=transfer.date,
        )
        db.add(from_transaction)

        # Создаем транзакцию зачисления
        to_amount = transfer.amount
        if from_account.currency != to_account.currency and transfer.exchange_rate:
            to_amount = transfer.amount * transfer.exchange_rate

        to_transaction = Transaction(
            user_id=current_user.id,
            account_id=to_account.id,
            amount=to_amount,
            type="income",
            category="Transfer",
            description=transfer.description or f"Transfer from {from_account.name}",
            date=transfer.date,
        )
        db.add(to_transaction)

        # Обновляем балансы счетов
        from_account.balance -= transfer.amount
        to_account.balance += to_amount

        db.commit()
        return {"message": "Transfer completed successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to process transfer")
