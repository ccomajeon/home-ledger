from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth.routes import router as auth_router
from app.config import get_settings
from app.db.base import Base
from app.db.seed import seed_defaults
from app.db.session import SessionLocal
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
    with SessionLocal() as db:
        seed_defaults(db)
    yield


app = FastAPI(title="Home Ledger API", version="0.2.1", lifespan=lifespan)
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

frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dist.is_dir():
    assets = frontend_dist / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="frontend-assets")

    @app.get("/{path:path}", include_in_schema=False)
    async def frontend(path: str) -> FileResponse:
        if path.startswith(("api/", "auth/")):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        requested = (frontend_dist / path).resolve()
        if requested.is_file() and frontend_dist.resolve() in requested.parents:
            return FileResponse(requested)
        return FileResponse(frontend_dist / "index.html")
