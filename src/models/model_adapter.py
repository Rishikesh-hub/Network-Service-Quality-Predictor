"""
Model Adapter Module for Network Service Quality Predictor
Provides unified interface to the trained MLPClassifier inference artifact.
"""

from typing import Dict, Any, List, Optional
import os
import pickle
import numpy as np
import pandas as pd
import yaml

from src.features.feature_builder import EXACT_26_FEATURE_NAMES


MODEL_ARTIFACT_DEFAULT = os.path.join("models", "mlp_ann_final.pkl")
CONFIG_PATH_DEFAULT = os.path.join("configs", "model.yaml")


class ModelAdapter:
    """Isolates application and UI layers from concrete trained model binaries."""

    def __init__(self, artifact_path: str = MODEL_ARTIFACT_DEFAULT, config_path: str = CONFIG_PATH_DEFAULT):
        self.artifact_path = artifact_path
        self.config_path = config_path
        self._model = None
        self._config = None

    @property
    def config(self) -> Dict[str, Any]:
        if self._config is None:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f)
            else:
                self._config = {
                    "model": {
                        "name": "MLP / ANN Classifier",
                        "version": "mlp_ann_final",
                        "type": "MLPClassifier",
                        "architecture": [128, 64],
                        "threshold": 0.80,
                        "prediction_type": "current_state"
                    }
                }
        return self._config

    @property
    def model(self):
        if self._model is None:
            if not os.path.exists(self.artifact_path):
                raise FileNotFoundError(f"Model artifact not found at {self.artifact_path}")
            with open(self.artifact_path, "rb") as f:
                self._model = pickle.load(f)
        return self._model

    def validate_features(self, X: pd.DataFrame) -> None:
        """Verifies that X strictly adheres to the 26-feature contract."""
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Inference input must be a pandas DataFrame.")
        if X.shape[1] != 26:
            raise ValueError(f"Model expects 26 features, got {X.shape[1]}")
        if list(X.columns) != EXACT_26_FEATURE_NAMES:
            raise ValueError("Feature columns or ordering do not match trained model contract.")

    def predict_probability(self, X: pd.DataFrame) -> np.ndarray:
        """
        Computes P(degraded) for model input.
        Returns 1D array of probabilities in [0.0, 1.0].
        """
        self.validate_features(X)
        probs = self.model.predict_proba(X)[:, 1]
        assert ((probs >= 0.0) & (probs <= 1.0)).all(), "Computed probabilities outside [0, 1] range"
        return probs

    def predict(self, X: pd.DataFrame, threshold: Optional[float] = None) -> np.ndarray:
        """
        Computes binary prediction using decision threshold (default: 0.80).
        0 = NORMAL, 1 = DEGRADED.
        """
        if threshold is None:
            threshold = float(self.config.get("model", {}).get("threshold", 0.80))
        probs = self.predict_probability(X)
        return (probs >= threshold).astype(int)

    def metadata(self) -> Dict[str, Any]:
        """Returns model architecture, version, evaluated threshold and evaluation metadata."""
        return {
            "model_version": self.config.get("model", {}).get("version", "mlp_ann_final"),
            "model_type": "MLPClassifier",
            "architecture": [128, 64],
            "activation": "relu",
            "solver": "adam",
            "alpha": 0.001,
            "threshold": float(self.config.get("model", {}).get("threshold", 0.80)),
            "prediction_type": "current_state",
            "feature_count": 26,
            "validation_f1": 0.9511,
            "validation_far": 0.010488,
            "final_test_f1": 0.9648,
            "final_test_far": 0.011805
        }
