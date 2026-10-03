"""
Alerts endpoints.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.services.alert_service import BackendAlertService

router = APIRouter()
alert_service = BackendAlertService()


@router.get("/alerts")
def get_alerts(
    status: Optional[str] = Query(None, description="Filter status (e.g. ACTIVE)"),
    limit: int = Query(50, ge=1, le=500)
):
    try:
        return alert_service.get_alerts(status=status, limit=limit)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
