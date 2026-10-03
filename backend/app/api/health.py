"""
Health endpoint.
"""

from fastapi import APIRouter
from backend.app.config import settings
from backend.app.models.model_adapter import BackendModelAdapter

router = APIRouter()


@router.get("/health")
def health_check():
    adapter = BackendModelAdapter()
    meta = adapter.metadata()
    return {
        "status": "ok",
        "model_loaded": True,
        "model_version": meta["model_version"],
        "architecture": meta["architecture"],
        "threshold": meta["threshold"],
        "prediction_type": meta["prediction_type"],
        "feature_count": meta["feature_count"]
    }
