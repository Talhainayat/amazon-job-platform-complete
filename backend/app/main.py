import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.base_class import Base
from app.db.schema_sync import sync_sqlite_schema
from app.db.seed import seed_if_needed
from app.db.session import SessionLocal, engine
from app.workers.scheduler import start_job_monitor, stop_job_monitor
from app import models  # noqa: F401

logger = logging.getLogger("job_platform")
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    sync_sqlite_schema(engine)
    db: Session = SessionLocal()
    try:
        seed_if_needed(db)
    except Exception:
        logger.exception("Demo seed skipped due to an error")
        db.rollback()
    finally:
        db.close()
    start_job_monitor()
    yield
    stop_job_monitor()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = []
    for err in exc.errors():
        loc = " ".join(str(part) for part in err.get("loc", []) if part != "body")
        messages.append(f"{loc}: {err.get('msg')}".strip())
    return JSONResponse(status_code=422, content={"detail": messages[0] if len(messages) == 1 else messages})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, (str, list, dict)) else str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled request error: %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
def home():
    return {"status": "success", "message": "Job Platform API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(api_router)
