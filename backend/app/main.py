from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.routes.admin import router as admin_router
from app.routes.categories import router as categories_router
from app.routes.health import router as health_router
from app.routes.payment_methods import router as payment_methods_router
from app.routes.transactions import router as transactions_router
from app.utils.logging import setup_logging

settings = get_settings()
setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Home Ledger API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(categories_router)
app.include_router(payment_methods_router)
app.include_router(admin_router)


@app.get("/api/me", tags=["auth"])
async def me() -> dict[str, str]:
    # Session auth is not wired yet; default to closed.
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
