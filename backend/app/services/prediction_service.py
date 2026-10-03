"""
Prediction Service for FastAPI backend.
"""

from typing import Dict, Any, Optional
import pandas as pd
from backend.app.config import settings
from backend.app.models.model_adapter import BackendModelAdapter
from backend.app.features.feature_builder import BackendFeatureBuilder
from backend.app.explanations.explain import BackendExplainer
from backend.app.repositories.sqlite_repository import BackendSQLiteRepository


class BackendPredictionService:
    def __init__(self):
        self.model_adapter = BackendModelAdapter()
        self.feature_builder = BackendFeatureBuilder()
        self.explainer = BackendExplainer()
        self.repository = BackendSQLiteRepository()

    def predict_single(self, telemetry: Dict[str, Any], custom_threshold: Optional[float] = None) -> Dict[str, Any]:
        threshold = custom_threshold if custom_threshold is not None else settings.THRESHOLD

        # 1. Build and validate 26 features
        feature_df = self.feature_builder.build_from_raw_dict(telemetry)

        # 2. ANN Inference
        prob = float(self.model_adapter.predict_probability(feature_df)[0])

        # 3. Decision Rule: 0.80 threshold
        prediction = 1 if prob >= threshold else 0
        status = "DEGRADED" if prediction == 1 else "NORMAL"

        # 4. Explanations
        contributors = self.explainer.explain_instance(feature_df.iloc[0], top_k=5)

        # 5. Persist audit record
        link_str = str(telemetry.get("link", "UNKNOWN"))
        features_dict = {col: float(val) for col, val in feature_df.iloc[0].items()}
        try:
            pred_id = self.repository.record_prediction(
                record=telemetry,
                probability=prob,
                threshold=threshold,
                prediction=prediction,
                status=status,
                link=link_str,
                features_dict=features_dict,
                model_version=self.model_adapter.metadata()["model_version"]
            )
        except Exception:
            pred_id = None

        return {
            "prediction_id": pred_id,
            "probability": round(prob, 4),
            "threshold": threshold,
            "prediction": prediction,
            "status": status,
            "prediction_type": "current_state",
            "model_version": self.model_adapter.metadata()["model_version"],
            "contributors": contributors,
            "telemetry": telemetry
        }

    def get_metadata(self) -> Dict[str, Any]:
        return self.model_adapter.metadata()
