"""
Data Adapter Module for Network Service Quality Predictor
Handles ingestion, schema validation, timestamp parsing, and telemetry analysis.
"""

from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np


REQUIRED_RAW_COLUMNS = [
    "packet_loss", "jitter", "rtt", "outflow_Router",
    "inflow_Router", "resolve", "ttl", "probe_duration", "link"
]

EXPECTED_LINKS = [
    "R1-R2", "R1-R9", "R2-R3", "R2-R9", "R3-R4", "R3-R8",
    "R4-R5", "R4-R6", "R6-R5", "R7-R6", "R8-R6", "R8-R7", "R9-R8"
]


class DataAdapter:
    """Adapts raw datasets and individual telemetry payloads for model pipeline consumption."""

    def __init__(self, required_columns: Optional[List[str]] = None, valid_links: Optional[List[str]] = None):
        self.required_columns = required_columns or REQUIRED_RAW_COLUMNS
        self.valid_links = valid_links or EXPECTED_LINKS

    def validate_raw_record(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validates an individual telemetry record dictionary.
        Returns (is_valid, error_message).
        """
        for col in self.required_columns:
            if col not in record:
                return False, f"Missing required telemetry field: '{col}'"
            val = record[col]
            if val is None or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
                return False, f"Invalid value for field '{col}': {val}"

        link_val = str(record["link"]).strip()
        if link_val not in self.valid_links:
            return False, f"Unknown link '{link_val}'. Supported links: {self.valid_links}"

        return True, None

    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Validates that a DataFrame contains the required raw columns.
        """
        missing = [c for c in self.required_columns if c not in df.columns]
        if missing:
            return False, f"DataFrame missing required columns: {missing}"
        return True, None

    @staticmethod
    def parse_unix_timestamp(ts_series: pd.Series) -> pd.Series:
        """
        Converts Unix epoch seconds to datetime pandas series.
        Preserves true timestamp representation (2025-06-25 to 2025-07-02).
        """
        return pd.to_datetime(ts_series, unit="s")

    @classmethod
    def analyze_timestamps(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyzes timestamp quality, global intervals, and per-link sampling statistics.
        """
        if "timestamp" not in df.columns:
            raise ValueError("DataFrame must contain 'timestamp' column.")

        raw_ts = df["timestamp"]
        dt = cls.parse_unix_timestamp(raw_ts)
        temp_df = df.copy()
        temp_df["dt"] = dt
        temp_df = temp_df.sort_values(by="dt")

        global_diffs = temp_df["dt"].diff().dropna().dt.total_seconds()

        analysis = {
            "dtype": str(raw_ts.dtype),
            "min_raw": int(raw_ts.min()),
            "max_raw": int(raw_ts.max()),
            "nunique_raw": int(raw_ts.nunique()),
            "min_datetime": str(dt.min()),
            "max_datetime": str(dt.max()),
            "total_records": len(df),
            "global_median_interval_sec": float(global_diffs.median()) if not global_diffs.empty else 0.0,
            "global_min_interval_sec": float(global_diffs.min()) if not global_diffs.empty else 0.0,
            "global_max_interval_sec": float(global_diffs.max()) if not global_diffs.empty else 0.0,
            "per_link": {}
        }

        if "link" in temp_df.columns:
            for link_name in temp_df["link"].unique():
                link_df = temp_df[temp_df["link"] == link_name].sort_values(by="dt")
                diffs = link_df["dt"].diff().dropna().dt.total_seconds()
                analysis["per_link"][link_name] = {
                    "count": len(link_df),
                    "median_interval_sec": float(diffs.median()) if not diffs.empty else 0.0,
                    "min_interval_sec": float(diffs.min()) if not diffs.empty else 0.0,
                    "max_interval_sec": float(diffs.max()) if not diffs.empty else 0.0,
                }

        return analysis

    @classmethod
    def load_dataset(cls, filepath: str) -> pd.DataFrame:
        """Loads a dataset from CSV."""
        return pd.read_csv(filepath)
