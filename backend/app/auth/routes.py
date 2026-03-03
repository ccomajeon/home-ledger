from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.auth.oauth import generate_oauth_nonce, generate_oauth_state

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def auth_login() -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={
            "message": "OAuth flow is not implemented yet.",
            "state": generate_oauth_state(),
            "nonce": generate_oauth_nonce(),
        },
    )


@router.get("/callback")
async def auth_callback() -> JSONResponse:
    return JSONResponse(status_code=501, content={"message": "OAuth callback is not implemented yet."})

