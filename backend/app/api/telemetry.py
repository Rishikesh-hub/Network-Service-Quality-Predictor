"""
Telemetry endpoints.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.services.telemetry_service import BackendTelemetryService

router = APIRouter()
telemetry_service = BackendTelemetryService()


@router.get("/telemetry")
def get_telemetry_records(
    link: Optional[str] = Query(None, description="Optional link filter"),
    limit: int = Query(100, ge=1, le=1000, description="Max rows to return"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    try:
        return telemetry_service.query_telemetry(link=link, limit=limit, offset=offset)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
