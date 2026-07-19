from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.deps import get_current_owner
from app.db.audit import add_audit_log
from app.db.backup import create_backup, list_backups, restore_backup
from app.db.models import AllowedAccount, AuditLog
from app.db.session import get_db
from app.schemas import (
    AccountCreate,
    AccountPublic,
    AccountUpdate,
    ApiMessage,
    AuditLogPublic,
    BackupPublic,
    RestoreRequest,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/accounts", response_model=list[AccountPublic])
def list_accounts(
    _: AllowedAccount = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> list[AllowedAccount]:
    return list(db.scalars(select(AllowedAccount).order_by(AllowedAccount.email)))


@router.post(
    "/accounts",
    response_model=AccountPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    body: AccountCreate,
    owner: AllowedAccount = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> AllowedAccount:
    email = body.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=422, detail="A valid email address is required")
    account = AllowedAccount(email=email, role=body.role, enabled=True)
    db.add(account)
    add_audit_log(
        db, owner.email, "account.create", {"email": email, "role": body.role}
    )
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Account already exists") from exc
    db.refresh(account)
    return account


@router.patch("/accounts/{account_id}", response_model=AccountPublic)
def update_account(
    account_id: int,
    body: AccountUpdate,
    owner: AllowedAccount = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> AllowedAccount:
    account = db.get(AllowedAccount, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    changes = body.model_dump(exclude_unset=True)
    if account.id == owner.id and (
        changes.get("enabled") is False or changes.get("role") == "USER"
    ):
        raise HTTPException(
            status_code=400, detail="You cannot remove your own owner access"
        )
    for key, value in changes.items():
        setattr(account, key, value)
    add_audit_log(db, owner.email, "account.update", {"id": account_id, **changes})
    db.commit()
    db.refresh(account)
    return account


@router.get("/audit-logs", response_model=list[AuditLogPublic])
def get_audit_logs(
    limit: int = Query(default=100, ge=1, le=1000),
    _: AllowedAccount = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> list[AuditLog]:
    stmt = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
    return list(db.scalars(stmt))


@router.get("/backups", response_model=list[BackupPublic])
def get_backups(_: AllowedAccount = Depends(get_current_owner)) -> list[BackupPublic]:
    try:
        return list_backups()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/backups", response_model=BackupPublic, status_code=status.HTTP_201_CREATED
)
def backup_database(_: AllowedAccount = Depends(get_current_owner)) -> BackupPublic:
    try:
        return create_backup()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/restore", response_model=ApiMessage)
def restore_database(
    body: RestoreRequest,
    _: AllowedAccount = Depends(get_current_owner),
    db: Session = Depends(get_db),
) -> ApiMessage:
    db.close()
    try:
        restore_backup(body.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Backup not found") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApiMessage(message="Database restored")
