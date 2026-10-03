"""
Feature Builder for FastAPI backend.
Constructs and validates the 26-feature model vector from raw telemetry inputs.
"""

from typing import Dict, Any, List, Optional
import os
import pickle
import numpy as np
import pandas as pd
from backend.app.config import settings
from backend.app.models.model_adapter import EXACT_26_FEATURE_NAMES


EXPECTED_LINKS = [
    "R1-R2", "R1-R9", "R2-R3", "R2-R9", "R3-R4", "R3-R8",
    "R4-R5", "R4-R6", "R6-R5", "R7-R6", "R8-R6", "R8-R7", "R9-R8"
]

REQUIRED_RAW_FIELDS = [
    "packet_loss", "jitter", "rtt", "outflow_Router",
    "inflow_Router", "resolve", "ttl", "probe_duration", "link"
]


class BackendFeatureBuilder:
    def __init__(self, preprocessor_path: Optional[str] = None):
        self.preprocessor_path = preprocessor_path or settings.PREPROCESSOR_PATH
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
    def derive_temporal(df: pd.DataFrame, reference_datetime: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        out = df.copy()
        if "timestamp" in out.columns:
            out["datetime"] = pd.to_datetime(out["timestamp"], unit="s")
        elif "datetime" not in out.columns:
            out["datetime"] = reference_datetime or pd.Timestamp.now()

        out["hour"] = out["datetime"].dt.hour
        out["day_of_week"] = out["datetime"].dt.dayofweek
        out["is_weekend"] = (out["day_of_week"] >= 5).astype(int)
        out["hour_sin"] = np.sin(2 * np.pi * out["hour"] / 24.0)
        out["hour_cos"] = np.cos(2 * np.pi * out["hour"] / 24.0)
        return out

    def build_from_raw_dict(self, record: Dict[str, Any]) -> pd.DataFrame:
        for f in REQUIRED_RAW_FIELDS:
            if f not in record:
                raise ValueError(f"Missing required field: '{f}'")
            val = record[f]
            if val is None or (isinstance(val, float) and (np.isinf(val))):
                raise ValueError(f"Invalid non-finite value for field '{f}': {val}")

        link_val = str(record["link"]).strip()
        if link_val not in EXPECTED_LINKS:
            raise ValueError(f"Unknown link '{link_val}'. Supported links: {EXPECTED_LINKS}")

        df_single = pd.DataFrame([record])
        df_temporal = self.derive_temporal(df_single)
        drop_cols = ["LABEL", "degradation", "timestamp", "datetime", "avalability"]
        clean_input = df_temporal.drop(columns=[c for c in drop_cols if c in df_temporal.columns])

        transformed = self.preprocessor.transform(clean_input)
        feature_df = pd.DataFrame(transformed, columns=self.preprocessor.get_feature_names_out())
        feature_df = feature_df[EXACT_26_FEATURE_NAMES]

        if feature_df.isnull().values.any():
            raise ValueError("Feature vector contains unexpected NaNs after preprocessing.")

        return feature_df
