import json

from sqlalchemy.orm import Session

from app.db.models import AuditLog


def add_audit_log(
    db: Session, actor_email: str, action: str, payload: dict[str, object]
) -> None:
    db.add(
        AuditLog(
            actor_email=actor_email,
            action=action,
            payload=json.dumps(payload, ensure_ascii=False, default=str),
        )
    )
