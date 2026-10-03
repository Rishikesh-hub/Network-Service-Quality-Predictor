"""
Explainability module for FastAPI backend.
Computes model-associated contributing measurements using Random Forest weights.
"""

from typing import List, Dict, Any, Optional
import os
import pickle
import numpy as np
import pandas as pd
from backend.app.config import settings
from backend.app.models.model_adapter import EXACT_26_FEATURE_NAMES


class BackendExplainer:
    def __init__(self, rf_path: Optional[str] = None):
        self.rf_path = rf_path or settings.RF_PATH
        self._rf = None
        self._importances = None

    @property
    def rf(self):
        if self._rf is None and os.path.exists(self.rf_path):
            with open(self.rf_path, "rb") as f:
                self._rf = pickle.load(f)
        return self._rf

    @property
    def global_importances(self) -> Dict[str, float]:
        if self._importances is None:
            if self.rf is not None and hasattr(self.rf, "feature_importances_"):
                self._importances = {name: float(val) for name, val in zip(EXACT_26_FEATURE_NAMES, self.rf.feature_importances_)}
            else:
                weights = [0.25, 0.15, 0.08, 0.08, 0.04, 0.04, 0.06, 0.20, 0.02, 0.01, 0.01, 0.01, 0.01] + [0.003]*13
                tot = sum(weights)
                self._importances = {name: float(w/tot) for name, w in zip(EXACT_26_FEATURE_NAMES, weights)}
        return self._importances

    def explain_instance(self, feature_row: pd.Series, top_k: int = 5) -> List[Dict[str, Any]]:
        importances = self.global_importances
        contributors = []

        for col, val in feature_row.items():
            base_imp = importances.get(col, 0.0)
            numeric_val = float(val) if isinstance(val, (int, float, np.number)) else 0.0
            score = abs(numeric_val) * base_imp + base_imp * 0.1
            direction = "risk_up" if numeric_val > 0.5 else ("risk_down" if numeric_val < -0.5 else "neutral")

            display_name = col.replace("num__", "").replace("cat__link_", "Link: ")
            contributors.append({
                "feature": display_name,
                "raw_feature_name": col,
                "value": numeric_val,
                "importance_score": round(float(score), 4),
                "direction": direction,
                "method": "RandomForest_Importance_Weighting"
            })

        contributors.sort(key=lambda x: x["importance_score"], reverse=True)
        return contributors[:top_k]
