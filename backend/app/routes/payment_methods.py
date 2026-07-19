from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.deps import get_current_account
from app.db.audit import add_audit_log
from app.db.models import AllowedAccount, PaymentMethod
from app.db.session import get_db
from app.schemas import NamedItemCreate, NamedItemPublic, NamedItemUpdate

router = APIRouter(prefix="/api/payment-methods", tags=["payment_methods"])


@router.get("", response_model=list[NamedItemPublic])
def list_payment_methods(
    include_disabled: bool = Query(False),
    _: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> list[PaymentMethod]:
    stmt = select(PaymentMethod).order_by(PaymentMethod.name)
    if not include_disabled:
        stmt = stmt.where(PaymentMethod.enabled.is_(True))
    return list(db.scalars(stmt))


@router.post("", response_model=NamedItemPublic, status_code=status.HTTP_201_CREATED)
def create_payment_method(
    body: NamedItemCreate,
    account: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> PaymentMethod:
    payment_method = PaymentMethod(name=body.name.strip())
    db.add(payment_method)
    add_audit_log(
        db, account.email, "payment_method.create", {"name": payment_method.name}
    )
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Payment method already exists"
        ) from exc
    db.refresh(payment_method)
    return payment_method


@router.patch("/{payment_method_id}", response_model=NamedItemPublic)
def update_payment_method(
    payment_method_id: int,
    body: NamedItemUpdate,
    account: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> PaymentMethod:
    payment_method = db.get(PaymentMethod, payment_method_id)
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    changes = body.model_dump(exclude_unset=True)
    if "name" in changes:
        changes["name"] = changes["name"].strip()
    for key, value in changes.items():
        setattr(payment_method, key, value)
    add_audit_log(
        db, account.email, "payment_method.update", {"id": payment_method_id, **changes}
    )
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Payment method already exists"
        ) from exc
    db.refresh(payment_method)
    return payment_method
