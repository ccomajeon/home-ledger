from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import AllowedAccount, Category, PaymentMethod

DEFAULT_CATEGORIES = ["식비", "주거/공과금", "교통", "의료", "저축", "급여", "기타"]
DEFAULT_PAYMENT_METHODS = ["카드", "현금", "계좌이체"]


def seed_defaults(db: Session) -> None:
    for name in DEFAULT_CATEGORIES:
        exists = db.scalar(select(Category).where(Category.name == name))
        if not exists:
            db.add(Category(name=name))

    for name in DEFAULT_PAYMENT_METHODS:
        exists = db.scalar(select(PaymentMethod).where(PaymentMethod.name == name))
        if not exists:
            db.add(PaymentMethod(name=name))

    owner_email = get_settings().owner_email.strip().lower()
    if owner_email:
        owner = db.scalar(
            select(AllowedAccount).where(AllowedAccount.email == owner_email)
        )
        if not owner:
            db.add(AllowedAccount(email=owner_email, role="OWNER", enabled=True))

    db.commit()
