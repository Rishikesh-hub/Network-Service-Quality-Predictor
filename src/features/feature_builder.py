"""
Feature Builder Module for Network Service Quality Predictor
Centralizes the 26-feature contract validation and construction.
"""

from typing import Dict, Any, List, Union, Optional
import pandas as pd
import numpy as np

from src.data.preprocessing import TelemetryPreprocessor
from src.data.data_adapter import DataAdapter, EXPECTED_LINKS


EXACT_26_FEATURE_NAMES = [
    "num__packet_loss",
    "num__jitter",
    "num__outflow_Router",
    "num__inflow_Router",
    "num__resolve",
    "num__ttl",
    "num__probe_duration",
    "num__rtt",
    "num__hour",
    "num__day_of_week",
    "num__is_weekend",
    "num__hour_sin",
    "num__hour_cos",
    "cat__link_R1-R2",
    "cat__link_R1-R9",
    "cat__link_R2-R3",
    "cat__link_R2-R9",
    "cat__link_R3-R4",
    "cat__link_R3-R8",
    "cat__link_R4-R5",
    "cat__link_R4-R6",
    "cat__link_R6-R5",
    "cat__link_R7-R6",
    "cat__link_R8-R6",
    "cat__link_R8-R7",
    "cat__link_R9-R8"
]


class FeatureBuilder:
    """Builds and validates the exact 26-feature model input vector from raw telemetry."""

    def __init__(self, preprocessor: Optional[TelemetryPreprocessor] = None):
        self.preprocessor = preprocessor or TelemetryPreprocessor()
        self.data_adapter = DataAdapter()

    @staticmethod
    def get_expected_feature_names() -> List[str]:
        return list(EXACT_26_FEATURE_NAMES)

    def validate_feature_contract(self, X: pd.DataFrame) -> None:
        """
        Validates that X matches the strict 26-feature contract.
        Raises ValueError if column count, order, or names do not match.
        """
        if not isinstance(X, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(X).__name__}")

        if X.shape[1] != 26:
            raise ValueError(f"Feature count mismatch: expected 26 features, got {X.shape[1]}")

        actual_cols = list(X.columns)
        if actual_cols != EXACT_26_FEATURE_NAMES:
            mismatches = [(i, exp, act) for i, (exp, act) in enumerate(zip(EXACT_26_FEATURE_NAMES, actual_cols)) if exp != act]
            raise ValueError(f"Feature contract mismatch: column order or names differ from trained contract: {mismatches}")

        if X.isnull().values.any():
            raise ValueError("Feature matrix contains unexpected NaN values after preprocessing.")

    def build_from_raw_dict(self, record: Dict[str, Any], timestamp: Optional[Any] = None) -> pd.DataFrame:
        """
        Constructs the 26-feature vector from a single raw dictionary of the 9 user inputs.
        """
        is_valid, err = self.data_adapter.validate_raw_record(record)
        if not is_valid:
            raise ValueError(f"Input validation error: {err}")

        df_single = pd.DataFrame([record])
        if timestamp is not None:
            df_single["timestamp"] = timestamp

        feature_df = self.preprocessor.transform_to_features(df_single)
        # Ensure column order matches exact contract
        feature_df = feature_df[EXACT_26_FEATURE_NAMES]
        self.validate_feature_contract(feature_df)
        return feature_df

    def build_from_raw_df(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """
        Constructs the 26-feature matrix from a DataFrame of raw telemetry records.
        """
        is_valid, err = self.data_adapter.validate_dataframe(raw_df)
        if not is_valid:
            raise ValueError(f"DataFrame validation error: {err}")

        # Check unknown links
        unsupported = set(raw_df["link"].dropna().unique()) - set(EXPECTED_LINKS)
        if unsupported:
            raise ValueError(f"Unknown link(s) detected: {unsupported}. Expected one of: {EXPECTED_LINKS}")

        feature_df = self.preprocessor.transform_to_features(raw_df)
        feature_df = feature_df[EXACT_26_FEATURE_NAMES]
        self.validate_feature_contract(feature_df)
        return feature_df
