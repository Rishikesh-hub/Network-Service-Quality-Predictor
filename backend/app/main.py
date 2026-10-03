"""
FastAPI Main Application Entrypoint for Network Service Quality Predictor (NSQP).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api import health, prediction, telemetry, alerts, metrics, boundary

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI service for current-state QoS degradation classification using tuned ANN (128, 64) and operating threshold 0.80.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health.router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(prediction.router, prefix=settings.API_V1_STR, tags=["Prediction"])
app.include_router(telemetry.router, prefix=settings.API_V1_STR, tags=["Telemetry"])
app.include_router(alerts.router, prefix=settings.API_V1_STR, tags=["Alerts"])
app.include_router(metrics.router, prefix=settings.API_V1_STR, tags=["Metrics"])
app.include_router(boundary.router, prefix=settings.API_V1_STR, tags=["Boundary Tests"])


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_V1_STR,
        "prediction_type": "current_state",
        "operating_threshold": settings.THRESHOLD
    }
