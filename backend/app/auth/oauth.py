from __future__ import annotations

import secrets
from dataclasses import dataclass

import httpx

from app.config import get_settings


@dataclass(frozen=True)
class GoogleUser:
    email: str
    email_verified: bool


def generate_oauth_state() -> str:
    return secrets.token_urlsafe(32)


def generate_oauth_nonce() -> str:
    return secrets.token_urlsafe(32)


async def exchange_code_for_user(code: str) -> GoogleUser:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=15) as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")
        if not access_token:
            raise ValueError("Google did not return an access token")

        user_response = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_response.raise_for_status()
        payload = user_response.json()

    email = payload.get("email")
    if not isinstance(email, str):
        raise ValueError("Google account has no email address")
    return GoogleUser(
        email=email.strip().lower(),
        email_verified=payload.get("email_verified") is True,
    )
