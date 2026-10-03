"""
Model Adapter for FastAPI backend.
Loads trained MLPClassifier inference artifact.
"""

from typing import Dict, Any, Optional
import os
import pickle
import numpy as np
import pandas as pd
from backend.app.config import settings


EXACT_26_FEATURE_NAMES = [
    "num__packet_loss", "num__jitter", "num__outflow_Router", "num__inflow_Router",
    "num__resolve", "num__ttl", "num__probe_duration", "num__rtt", "num__hour",
    "num__day_of_week", "num__is_weekend", "num__hour_sin", "num__hour_cos",
    "cat__link_R1-R2", "cat__link_R1-R9", "cat__link_R2-R3", "cat__link_R2-R9",
    "cat__link_R3-R4", "cat__link_R3-R8", "cat__link_R4-R5", "cat__link_R4-R6",
    "cat__link_R6-R5", "cat__link_R7-R6", "cat__link_R8-R6", "cat__link_R8-R7",
    "cat__link_R9-R8"
]


class BackendModelAdapter:
    def __init__(self, artifact_path: Optional[str] = None):
        self.artifact_path = artifact_path or settings.MODEL_PATH
        self._model = None

    @property
    def model(self):
        if self._model is None:
            if not os.path.exists(self.artifact_path):
                raise FileNotFoundError(f"Model artifact not found at: {self.artifact_path}")
            with open(self.artifact_path, "rb") as f:
                self._model = pickle.load(f)
        return self._model

    def validate_features(self, X: pd.DataFrame) -> None:
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Model input must be a pandas DataFrame.")
        if X.shape[1] != 26:
            raise ValueError(f"Model expects 26 features, received {X.shape[1]}")
        if list(X.columns) != EXACT_26_FEATURE_NAMES:
            raise ValueError("Feature columns or order do not match the exact 26-feature trained contract.")

    def predict_probability(self, X: pd.DataFrame) -> np.ndarray:
        self.validate_features(X)
        probs = self.model.predict_proba(X)[:, 1]
        assert ((probs >= 0.0) & (probs <= 1.0)).all()
        return probs

    def predict(self, X: pd.DataFrame, threshold: Optional[float] = None) -> np.ndarray:
        th = threshold if threshold is not None else settings.THRESHOLD
        probs = self.predict_probability(X)
        return (probs >= th).astype(int)

    def metadata(self) -> Dict[str, Any]:
        return {
            "model_version": "mlp_ann_final",
            "model_type": "MLPClassifier",
            "architecture": [128, 64],
            "activation": "relu",
            "solver": "adam",
            "alpha": 0.001,
            "threshold": settings.THRESHOLD,
            "prediction_type": "current_state",
            "feature_count": 26,
            "validation_f1": 0.9511,
            "validation_far": 0.010488,
            "final_test_f1": 0.9648,
            "final_test_far": 0.011805
        }
