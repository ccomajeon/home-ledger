from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.crud import get_allowed_account_by_email
from app.db.models import AllowedAccount
from app.db.session import get_db
from app.utils.security import read_session_token


def raise_unauthorized() -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
    )


def get_current_account(
    request: Request,
    db: Session = Depends(get_db),
) -> AllowedAccount:
    token = request.cookies.get(get_settings().session_cookie_name)
    email = read_session_token(token) if token else None
    if not email:
        raise_unauthorized()

    account = get_allowed_account_by_email(db, email)
    if not account or not account.enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is not allowed"
        )
    return account


def get_current_owner(
    account: AllowedAccount = Depends(get_current_account),
) -> AllowedAccount:
    if account.role != "OWNER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Owner role required"
        )
    return account
