"""
Telemetry Service for FastAPI backend.
Handles querying historical telemetry dataset without loading 180k rows into browser memory.
"""

from typing import Dict, Any, List, Optional
import os
import pandas as pd
from backend.app.config import settings


class BackendTelemetryService:
    def __init__(self, csv_path: Optional[str] = None):
        self.csv_path = csv_path or settings.PRIMARY_DATASET_CSV
        self._df = None

    @property
    def df(self):
        if self._df is None:
            if not os.path.exists(self.csv_path):
                # Fallback to alternate relative path
                alt = os.path.join("data", "network_qos_preprocessed", "qos_labeled_cleaned.csv")
                if os.path.exists(alt):
                    self.csv_path = alt
                else:
                    alt2 = os.path.join("network_qos_preprocessed", "qos_labeled_cleaned.csv")
                    if os.path.exists(alt2):
                        self.csv_path = alt2
                    else:
                        raise FileNotFoundError(f"Telemetry dataset not found at: {self.csv_path}")
            self._df = pd.read_csv(self.csv_path)
            if "timestamp" in self._df.columns and "datetime" not in self._df.columns:
                self._df["datetime"] = pd.to_datetime(self._df["timestamp"], unit="s").astype(str)
        return self._df

    def query_telemetry(self, link: Optional[str] = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        data = self.df
        if link and link != "ALL":
            data = data[data["link"] == link]

        total_matching = len(data)
        page = data.iloc[offset:offset+limit]

        cols = ["timestamp", "datetime", "link", "packet_loss", "jitter", "rtt", "outflow_Router", "inflow_Router", "resolve", "ttl", "probe_duration", "degradation"]
        available_cols = [c for c in cols if c in page.columns]
        records = page[available_cols].to_dict(orient="records")

        # Basic summary stats on sampled data
        num_cols = ["packet_loss", "jitter", "rtt", "outflow_Router", "inflow_Router"]
        stats = {}
        for c in num_cols:
            if c in data.columns:
                stats[c] = {
                    "mean": round(float(data[c].mean()), 4),
                    "median": round(float(data[c].median()), 4),
                    "min": round(float(data[c].min()), 4),
                    "max": round(float(data[c].max()), 4),
                    "std": round(float(data[c].std()), 4)
                }

        unique_links = sorted(list(self.df["link"].dropna().unique()))

        return {
            "total": total_matching,
            "limit": limit,
            "offset": offset,
            "records": records,
            "summary_stats": stats,
            "links": unique_links
        }
