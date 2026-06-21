"""
VisionGuard AI — FastAPI entrypoint.

Run with:
    uvicorn app.main:app --reload --port 8000

Interactive API docs: http://localhost:8000/docs
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.api import detect, evidence, analytics, violations

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("visionguard")

app = FastAPI(
    title="VisionGuard AI",
    description="Intelligent Traffic Violation Enforcement Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("VisionGuard AI backend ready.")
    # Pre-warm the detector at startup rather than on first request, so
    # the officer's first upload isn't slowed down by model load time.
    try:
        from app.detection.detector import get_detector

        detector = get_detector()
        logger.info("Detector mode: %s", detector.mode)
    except Exception as exc:  # pragma: no cover
        logger.error("Detector failed to load at startup: %s", exc)


app.include_router(detect.router)
app.include_router(evidence.router)
app.include_router(analytics.router)
app.include_router(violations.router)

app.mount("/storage", StaticFiles(directory=str(settings.STORAGE_DIR)), name="storage")


@app.get("/api/health")
def health():
    from app.detection.detector import get_detector
    from app.violations.engine import get_engine

    detector = get_detector()
    engine = get_engine()
    return {
        "status": "ok",
        "detector_mode": detector.mode,
        "implemented_modules": engine.implemented_modules(),
        "architecture_modules": engine.architecture_modules(),
    }
