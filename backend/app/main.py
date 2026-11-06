from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import api_router
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa: F401

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AETHRIX AI - Independent, Free-to-Use AI Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # Keep API available even if DB bootstrap fails in constrained environments.
        pass

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to AETHRIX AI", "status": "operational"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
