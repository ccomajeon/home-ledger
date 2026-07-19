from __future__ import annotations

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pwdlib import PasswordHash

from app.config import get_settings

OAUTH_STATE_COOKIE = "home_ledger_oauth_state"
password_hash = PasswordHash.recommended()


def _serializer(salt: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(get_settings().session_secret, salt=salt)


def cookie_secure() -> bool:
    return get_settings().is_production


def create_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    return password_hash.verify(password, encoded_hash)


def create_session_token(email: str) -> str:
    return _serializer("session").dumps({"email": email.strip().lower()})


def read_session_token(token: str) -> str | None:
    try:
        data = _serializer("session").loads(
            token,
            max_age=get_settings().session_max_age_seconds,
        )
    except (BadSignature, SignatureExpired):
        return None
    email = data.get("email") if isinstance(data, dict) else None
    return email if isinstance(email, str) else None


def create_oauth_state_token(state: str, nonce: str) -> str:
    return _serializer("oauth-state").dumps({"state": state, "nonce": nonce})


def read_oauth_state_token(token: str, max_age: int = 600) -> tuple[str, str] | None:
    try:
        data = _serializer("oauth-state").loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    if not isinstance(data, dict):
        return None
    state = data.get("state")
    nonce = data.get("nonce")
    if not isinstance(state, str) or not isinstance(nonce, str):
        return None
    return state, nonce
