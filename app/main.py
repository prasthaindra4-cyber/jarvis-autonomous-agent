import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

# Logging configuration
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("jarvis.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"✨ {settings.APP_NAME} started in {settings.ENVIRONMENT} mode.")
    logger.info("Ready to accept autonomous multi-agent tasks.")
    yield
    logger.info(f"🛑 {settings.APP_NAME} shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend Autonomous Multi-Agent AI System (JARVIS-like Architecture)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes
app.include_router(api_router, prefix="/api/v1")

# Mount static assets
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", summary="JARVIS Command Center Dashboard")
async def root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/dashboard", summary="JARVIS Command Center Dashboard Alternative Link")
async def dashboard():
    index_file = os.path.join(static_dir, "index.html")
    return FileResponse(index_file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
