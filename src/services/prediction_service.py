"""
Prediction Service Module for Network Service Quality Predictor
Orchestrates validation, feature engineering, model inference, thresholding, explanation, and persistence.
"""

from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

from src.features.feature_builder import FeatureBuilder
from src.models.model_adapter import ModelAdapter
from src.explanations.explain import ContributorExplainer
from src.repositories.sqlite_repository import SQLiteRepository


class PredictionService:
    """Core service for current-state QoS degradation predictions."""

    def __init__(self,
                 feature_builder: Optional[FeatureBuilder] = None,
                 model_adapter: Optional[ModelAdapter] = None,
                 explainer: Optional[ContributorExplainer] = None,
                 repository: Optional[SQLiteRepository] = None):
        self.feature_builder = feature_builder or FeatureBuilder()
        self.model_adapter = model_adapter or ModelAdapter()
        self.explainer = explainer or ContributorExplainer()
        self.repository = repository or SQLiteRepository()

    def predict_single(self, telemetry: Dict[str, Any], custom_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Runs complete inference pipeline on a single raw telemetry record.
        Strictly enforces threshold = 0.80 by default.
        """
        threshold = custom_threshold if custom_threshold is not None else float(self.model_adapter.config.get("model", {}).get("threshold", 0.80))

        # 1. Build and validate 26 features
        feature_df = self.feature_builder.build_from_raw_dict(telemetry)

        # 2. ANN Inference
        prob = float(self.model_adapter.predict_probability(feature_df)[0])

        # 3. Decision Rule
        prediction = 1 if prob >= threshold else 0
        status = "DEGRADED" if prediction == 1 else "NORMAL"

        # 4. Explanations (Model-associated contributing measurements)
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
            "probability": prob,
            "threshold": threshold,
            "prediction": prediction,
            "status": status,
            "prediction_type": "current_state",
            "model_version": self.model_adapter.metadata()["model_version"],
            "contributors": contributors,
            "telemetry": telemetry,
            "feature_vector": features_dict
        }

    def predict_batch(self, df_raw: pd.DataFrame, custom_threshold: Optional[float] = None) -> pd.DataFrame:
        """
        Vectorized batch inference on a DataFrame of raw telemetry.
        """
        threshold = custom_threshold if custom_threshold is not None else float(self.model_adapter.config.get("model", {}).get("threshold", 0.80))

        # Build 26-feature matrix
        feature_df = self.feature_builder.build_from_raw_df(df_raw)

        # Predict probabilities
        probs = self.model_adapter.predict_probability(feature_df)
        preds = (probs >= threshold).astype(int)
        statuses = np.where(preds == 1, "DEGRADED", "NORMAL")

        result_df = df_raw.copy()
        result_df["probability"] = probs
        result_df["prediction"] = preds
        result_df["status"] = statuses
        result_df["threshold"] = threshold
        result_df["prediction_type"] = "current_state"
        return result_df

    def get_metadata(self) -> Dict[str, Any]:
        """Returns model metadata and evaluated metrics."""
        return self.model_adapter.metadata()
