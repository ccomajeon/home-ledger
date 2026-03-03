from fastapi import HTTPException, status


def raise_unauthorized() -> None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

