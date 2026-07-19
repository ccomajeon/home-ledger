from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, case, func, or_, select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_account
from app.db.audit import add_audit_log
from app.db.models import AllowedAccount, Category, PaymentMethod, Transaction
from app.db.session import get_db
from app.schemas import (
    ApiMessage,
    TransactionCreate,
    TransactionPublic,
    TransactionSummary,
    TransactionUpdate,
)

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def _transaction_query() -> Select[tuple[Transaction, str, str]]:
    return (
        select(Transaction, Category.name, PaymentMethod.name)
        .join(Category, Transaction.category_id == Category.id)
        .join(PaymentMethod, Transaction.payment_method_id == PaymentMethod.id)
    )


def _filters(
    stmt: Select,
    start_date: date | None,
    end_date: date | None,
    tx_type: str | None,
    category_id: int | None,
    payment_method_id: int | None,
    search: str | None,
) -> Select:
    if start_date:
        stmt = stmt.where(Transaction.tx_date >= start_date)
    if end_date:
        stmt = stmt.where(Transaction.tx_date <= end_date)
    if tx_type:
        stmt = stmt.where(Transaction.tx_type == tx_type)
    if category_id:
        stmt = stmt.where(Transaction.category_id == category_id)
    if payment_method_id:
        stmt = stmt.where(Transaction.payment_method_id == payment_method_id)
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Transaction.description.ilike(pattern),
                Category.name.ilike(pattern),
                PaymentMethod.name.ilike(pattern),
            )
        )
    return stmt


def _public(row: tuple[Transaction, str, str]) -> TransactionPublic:
    transaction, category_name, payment_method_name = row
    return TransactionPublic(
        id=transaction.id,
        tx_date=transaction.tx_date,
        amount=transaction.amount,
        tx_type=transaction.tx_type,
        description=transaction.description,
        category_id=transaction.category_id,
        category_name=category_name,
        payment_method_id=transaction.payment_method_id,
        payment_method_name=payment_method_name,
        created_at=transaction.created_at,
    )


def _validate_references(db: Session, category_id: int, payment_method_id: int) -> None:
    category = db.get(Category, category_id)
    if not category or not category.enabled:
        raise HTTPException(status_code=422, detail="Category is not available")
    payment_method = db.get(PaymentMethod, payment_method_id)
    if not payment_method or not payment_method.enabled:
        raise HTTPException(status_code=422, detail="Payment method is not available")


@router.get("", response_model=list[TransactionPublic])
def list_transactions(
    start_date: date | None = None,
    end_date: date | None = None,
    tx_type: str | None = Query(default=None, pattern="^(INCOME|EXPENSE)$"),
    category_id: int | None = None,
    payment_method_id: int | None = None,
    search: str | None = Query(default=None, max_length=100),
    limit: int = Query(default=200, ge=1, le=1000),
    _: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> list[TransactionPublic]:
    stmt = _filters(
        _transaction_query(),
        start_date,
        end_date,
        tx_type,
        category_id,
        payment_method_id,
        search,
    )
    rows = db.execute(
        stmt.order_by(Transaction.tx_date.desc(), Transaction.id.desc()).limit(limit)
    )
    return [_public(row) for row in rows.tuples()]


@router.get("/summary", response_model=TransactionSummary)
def transaction_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    _: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> TransactionSummary:
    stmt = select(
        func.coalesce(
            func.sum(
                case((Transaction.tx_type == "INCOME", Transaction.amount), else_=0)
            ),
            0,
        ),
        func.coalesce(
            func.sum(
                case((Transaction.tx_type == "EXPENSE", Transaction.amount), else_=0)
            ),
            0,
        ),
    ).select_from(Transaction)
    if start_date:
        stmt = stmt.where(Transaction.tx_date >= start_date)
    if end_date:
        stmt = stmt.where(Transaction.tx_date <= end_date)
    income, expense = db.execute(stmt).one()
    income_value = Decimal(income)
    expense_value = Decimal(expense)
    return TransactionSummary(
        income=income_value,
        expense=expense_value,
        balance=income_value - expense_value,
    )


@router.post("", response_model=TransactionPublic, status_code=status.HTTP_201_CREATED)
def create_transaction(
    body: TransactionCreate,
    account: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> TransactionPublic:
    _validate_references(db, body.category_id, body.payment_method_id)
    transaction = Transaction(**body.model_dump())
    db.add(transaction)
    add_audit_log(
        db,
        account.email,
        "transaction.create",
        {"amount": body.amount, "tx_type": body.tx_type, "tx_date": body.tx_date},
    )
    db.commit()
    row = db.execute(_transaction_query().where(Transaction.id == transaction.id)).one()
    return _public(row)


@router.patch("/{transaction_id}", response_model=TransactionPublic)
def update_transaction(
    transaction_id: int,
    body: TransactionUpdate,
    account: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> TransactionPublic:
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    changes = body.model_dump(exclude_unset=True)
    _validate_references(
        db,
        changes.get("category_id", transaction.category_id),
        changes.get("payment_method_id", transaction.payment_method_id),
    )
    for key, value in changes.items():
        setattr(transaction, key, value)
    add_audit_log(
        db, account.email, "transaction.update", {"id": transaction_id, **changes}
    )
    db.commit()
    row = db.execute(_transaction_query().where(Transaction.id == transaction.id)).one()
    return _public(row)


@router.delete("/{transaction_id}", response_model=ApiMessage)
def delete_transaction(
    transaction_id: int,
    account: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> ApiMessage:
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(transaction)
    add_audit_log(db, account.email, "transaction.delete", {"id": transaction_id})
    db.commit()
    return ApiMessage(message="Transaction deleted")
