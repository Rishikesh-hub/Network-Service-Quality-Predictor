"""
Tests for Timestamp Interpretation and Verification.
Validates Unix epoch seconds conversion, per-link sampling intervals, and absence of 1970 artifacts.
"""

import pytest
import pandas as pd
import numpy as np
from src.data.data_adapter import DataAdapter


def test_unix_seconds_conversion():
    # Known dataset raw timestamp bounds
    raw_min = 1750858080
    raw_max = 1751465610

    series = pd.Series([raw_min, raw_max])
    converted = DataAdapter.parse_unix_timestamp(series)

    # 1750858080 in UTC/local is June 2025
    assert converted.iloc[0].year == 2025
    assert converted.iloc[0].month == 6
    assert converted.iloc[0].day == 25

    # 1751465610 is July 2025
    assert converted.iloc[1].year == 2025
    assert converted.iloc[1].month == 7
    assert converted.iloc[1].day == 2

    # Reject 1970 nanoseconds interpretation
    assert not (converted.dt.year == 1970).any()


def test_timestamp_analysis():
    # Create synthetic link telemetry with repeated timestamps across links and 15s intervals
    data = {
        "timestamp": [1750858080, 1750858080, 1750858095, 1750858095, 1750858110],
        "link": ["R1-R2", "R2-R3", "R1-R2", "R2-R3", "R1-R2"],
        "packet_loss": [0.1, 0.2, 0.1, 0.3, 0.1]
    }
    df = pd.DataFrame(data)
    analysis = DataAdapter.analyze_timestamps(df)

    assert analysis["min_raw"] == 1750858080
    assert analysis["max_raw"] == 1751465610 or analysis["max_raw"] == 1750858110
    # Link R1-R2 has 15s intervals
    assert "R1-R2" in analysis["per_link"]
    assert analysis["per_link"]["R1-R2"]["median_interval_sec"] == 15.0
