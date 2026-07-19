from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.deps import get_current_account
from app.db.audit import add_audit_log
from app.db.models import AllowedAccount, Category
from app.db.session import get_db
from app.schemas import NamedItemCreate, NamedItemPublic, NamedItemUpdate

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[NamedItemPublic])
def list_categories(
    include_disabled: bool = Query(False),
    _: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> list[Category]:
    stmt = select(Category).order_by(Category.name)
    if not include_disabled:
        stmt = stmt.where(Category.enabled.is_(True))
    return list(db.scalars(stmt))


@router.post("", response_model=NamedItemPublic, status_code=status.HTTP_201_CREATED)
def create_category(
    body: NamedItemCreate,
    account: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Category:
    category = Category(name=body.name.strip())
    db.add(category)
    add_audit_log(db, account.email, "category.create", {"name": category.name})
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category already exists") from exc
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=NamedItemPublic)
def update_category(
    category_id: int,
    body: NamedItemUpdate,
    account: AllowedAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> Category:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    changes = body.model_dump(exclude_unset=True)
    if "name" in changes:
        changes["name"] = changes["name"].strip()
    for key, value in changes.items():
        setattr(category, key, value)
    add_audit_log(db, account.email, "category.update", {"id": category_id, **changes})
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category already exists") from exc
    db.refresh(category)
    return category
