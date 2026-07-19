from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.deps import get_current_account
from app.auth.oauth import (
    exchange_code_for_user,
    generate_oauth_nonce,
    generate_oauth_state,
)
from app.config import get_settings
from app.db.audit import add_audit_log
from app.db.crud import get_allowed_account_by_email
from app.db.models import AllowedAccount
from app.db.session import get_db
from app.schemas import AccountPublic, AuthConfig, LocalLoginRequest
from app.utils.security import (
    OAUTH_STATE_COOKIE,
    cookie_secure,
    create_oauth_state_token,
    create_session_token,
    read_oauth_state_token,
    verify_password,
)

router = APIRouter(tags=["auth"])
LOGIN_WINDOW_SECONDS = 300
LOGIN_MAX_FAILURES = 5
_failed_logins: dict[str, deque[float]] = defaultdict(deque)
_failed_logins_lock = Lock()


def _set_session_cookie(response: Response, email: str) -> None:
    settings = get_settings()
    response.set_cookie(
        settings.session_cookie_name,
        create_session_token(email),
        max_age=settings.session_max_age_seconds,
        httponly=True,
        secure=cookie_secure(),
        samesite="lax",
    )


def _login_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _prune_failures(key: str, now: float) -> deque[float]:
    attempts = _failed_logins[key]
    while attempts and now - attempts[0] > LOGIN_WINDOW_SECONDS:
        attempts.popleft()
    return attempts


def _enforce_login_limit(key: str) -> None:
    with _failed_logins_lock:
        if len(_prune_failures(key, monotonic())) >= LOGIN_MAX_FAILURES:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Try again later.",
            )


def _record_login_failure(key: str) -> None:
    with _failed_logins_lock:
        _prune_failures(key, monotonic()).append(monotonic())


def _clear_login_failures(key: str) -> None:
    with _failed_logins_lock:
        _failed_logins.pop(key, None)


def _resolve_account(db: Session, email: str) -> AllowedAccount:
    settings = get_settings()
    normalized = email.strip().lower()
    account = get_allowed_account_by_email(db, normalized)

    if normalized == settings.owner_email.strip().lower():
        if not account:
            account = AllowedAccount(email=normalized, role="OWNER", enabled=True)
            db.add(account)
            db.commit()
            db.refresh(account)
        elif account.role != "OWNER":
            account.role = "OWNER"
            db.commit()
            db.refresh(account)
    elif not account and normalized.partition("@")[2] in settings.allowed_domains:
        account = AllowedAccount(email=normalized, role="USER", enabled=True)
        db.add(account)
        db.commit()
        db.refresh(account)

    if not account or not account.enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is not allowed"
        )
    return account


def _resolve_local_admin(db: Session) -> AllowedAccount:
    settings = get_settings()
    identity = settings.local_admin_identity.strip().lower()
    account = get_allowed_account_by_email(db, identity)
    if not account:
        account = AllowedAccount(email=identity, role="OWNER", enabled=True)
        db.add(account)
    else:
        account.role = "OWNER"
        account.enabled = True
    add_audit_log(
        db, identity, "auth.local_login", {"username": settings.local_admin_username}
    )
    db.commit()
    db.refresh(account)
    return account


@router.get("/api/auth/config", response_model=AuthConfig)
async def auth_config() -> AuthConfig:
    settings = get_settings()
    return AuthConfig(
        google_enabled=bool(
            settings.google_client_id and settings.google_client_secret
        ),
        local_admin_enabled=bool(
            settings.local_admin_enabled and settings.local_admin_password_hash
        ),
    )


@router.post("/auth/local-login", response_model=AccountPublic)
def local_login(
    body: LocalLoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> AllowedAccount:
    settings = get_settings()
    if not settings.local_admin_enabled or not settings.local_admin_password_hash:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    key = _login_key(request)
    _enforce_login_limit(key)
    username_matches = secrets_compare(
        body.username.strip().upper(),
        settings.local_admin_username.strip().upper(),
    )
    try:
        password_matches = verify_password(
            body.password.get_secret_value(),
            settings.local_admin_password_hash,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Local administrator login is misconfigured",
        ) from exc
    if not username_matches or not password_matches:
        _record_login_failure(key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    _clear_login_failures(key)
    account = _resolve_local_admin(db)
    _set_session_cookie(response, account.email)
    return account


@router.get("/auth/login")
async def auth_login() -> RedirectResponse:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    state = generate_oauth_state()
    nonce = generate_oauth_nonce()
    query = urlencode(
        {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "nonce": nonce,
            "prompt": "select_account",
        }
    )
    response = RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{query}")
    response.set_cookie(
        OAUTH_STATE_COOKIE,
        create_oauth_state_token(state, nonce),
        max_age=600,
        httponly=True,
        secure=cookie_secure(),
        samesite="lax",
    )
    return response


@router.get("/auth/callback")
async def auth_callback(
    request: Request,
    code: str = Query(min_length=1),
    state: str = Query(min_length=1),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    state_token = request.cookies.get(OAUTH_STATE_COOKIE, "")
    expected = read_oauth_state_token(state_token)
    if not expected or not secrets_compare(expected[0], state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state"
        )

    try:
        google_user = await exchange_code_for_user(code)
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google authentication failed",
        ) from exc
    if not google_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Email is not verified"
        )

    account = _resolve_account(db, google_user.email)
    response = RedirectResponse(get_settings().frontend_base_url)
    _set_session_cookie(response, account.email)
    response.delete_cookie(OAUTH_STATE_COOKIE)
    return response


def secrets_compare(left: str, right: str) -> bool:
    import secrets

    return secrets.compare_digest(left, right)


@router.post("/auth/dev-login")
async def dev_login(
    email: str | None = None,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    settings = get_settings()
    if settings.is_production or not settings.dev_auth_bypass:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    account = _resolve_account(db, email or settings.owner_email)
    response = RedirectResponse(
        settings.frontend_base_url, status_code=status.HTTP_303_SEE_OTHER
    )
    _set_session_cookie(response, account.email)
    return response


@router.post("/auth/logout")
async def logout() -> RedirectResponse:
    settings = get_settings()
    response = RedirectResponse(
        settings.frontend_base_url, status_code=status.HTTP_303_SEE_OTHER
    )
    response.delete_cookie(settings.session_cookie_name)
    return response


@router.get("/api/me", response_model=AccountPublic)
async def me(account: AllowedAccount = Depends(get_current_account)) -> AllowedAccount:
    return account
