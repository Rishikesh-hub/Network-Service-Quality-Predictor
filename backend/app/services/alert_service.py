"""
Alert Service for FastAPI backend.
"""

from typing import Dict, Any, List, Optional
from backend.app.repositories.sqlite_repository import BackendSQLiteRepository


class BackendAlertService:
    def __init__(self):
        self.repository = BackendSQLiteRepository()

    def get_alerts(self, status: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        alerts = self.repository.get_alerts(status=status, limit=limit)
        active_count = len([a for a in alerts if a.get("status") == "ACTIVE"])
        recent_preds = self.repository.get_recent_predictions(limit=limit)

        return {
            "alerts": alerts,
            "active_count": active_count,
            "recent_predictions": recent_preds
        }
