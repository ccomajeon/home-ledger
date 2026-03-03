from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models


def get_allowed_account_by_email(db: Session, email: str) -> models.AllowedAccount | None:
    stmt = select(models.AllowedAccount).where(models.AllowedAccount.email == email)
    return db.scalar(stmt)

