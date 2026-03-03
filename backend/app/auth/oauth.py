from __future__ import annotations

import secrets


def generate_oauth_state() -> str:
    return secrets.token_urlsafe(32)


def generate_oauth_nonce() -> str:
    return secrets.token_urlsafe(32)

