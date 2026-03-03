from app.config import get_settings


def cookie_secure() -> bool:
    return get_settings().is_production

