"""
Preprocessing Module for Network Service Quality Predictor
Handles temporal feature engineering and loads the fitted ColumnTransformer.
"""

from typing import Optional, Union, Dict, Any
from pathlib import Path
import os
import pickle
import numpy as np
import pandas as pd


PREPROCESSOR_PATH = os.path.join("models", "preprocessor.pkl")


class TelemetryPreprocessor:
    """Applies temporal feature engineering and fitted ColumnTransformer to telemetry data."""

    def __init__(self, preprocessor_path: str = PREPROCESSOR_PATH):
        self.preprocessor_path = preprocessor_path
        self._preprocessor = None

    @property
    def preprocessor(self):
        if self._preprocessor is None:
            if not os.path.exists(self.preprocessor_path):
                raise FileNotFoundError(f"Preprocessor artifact not found at {self.preprocessor_path}")
            with open(self.preprocessor_path, "rb") as f:
                self._preprocessor = pickle.load(f)
        return self._preprocessor

    @staticmethod
    def derive_temporal_features(df: pd.DataFrame, reference_datetime: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        """
        Derives hour, day_of_week, is_weekend, hour_sin, hour_cos.
        If 'timestamp' is present, converts via Unix seconds.
        If not, uses reference_datetime or current UTC time.
        """
        out = df.copy()
        if "timestamp" in out.columns:
            out["datetime"] = pd.to_datetime(out["timestamp"], unit="s")
        elif "datetime" not in out.columns:
            dt = reference_datetime or pd.Timestamp.now()
            out["datetime"] = dt

        out["hour"] = out["datetime"].dt.hour
        out["day_of_week"] = out["datetime"].dt.dayofweek
        out["is_weekend"] = (out["day_of_week"] >= 5).astype(int)
        out["hour_sin"] = np.sin(2 * np.pi * out["hour"] / 24.0)
        out["hour_cos"] = np.cos(2 * np.pi * out["hour"] / 24.0)
        return out

    def transform_to_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepares raw telemetry DataFrame and transforms it into the 26-feature model matrix.
        """
        df_temp = self.derive_temporal_features(df)
        drop_cols = ["LABEL", "degradation", "timestamp", "datetime", "avalability"]
        clean_input = df_temp.drop(columns=[c for c in drop_cols if c in df_temp.columns])

        transformed_matrix = self.preprocessor.transform(clean_input)
        feature_names = self.preprocessor.get_feature_names_out()
        return pd.DataFrame(transformed_matrix, columns=feature_names, index=df.index)
