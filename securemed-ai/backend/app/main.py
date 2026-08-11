import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine, SessionLocal
from app import models  # noqa: F401  (ensures models are registered before create_all)
from app.api import auth, ai, tenants, governance, security_center, audit, model_config, overview

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("securemed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    from app.seed import seed_if_empty

    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="SecureMed AI",
    description="Ethical AI & Multi-Tenant Security Governance Demonstration Platform. "
    "DEMO ENVIRONMENT — SYNTHETIC HEALTHCARE DATA — NOT FOR MEDICAL USE.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak stack traces, internal paths, or secrets to the client.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred. This has been logged."},
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "demo_mode": settings.demo_mode}


app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(tenants.router)
app.include_router(governance.router)
app.include_router(security_center.router)
app.include_router(audit.router)
app.include_router(model_config.router)
app.include_router(overview.router)
