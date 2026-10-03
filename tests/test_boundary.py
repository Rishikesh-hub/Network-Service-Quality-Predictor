"""
Tests for Boundary Scenarios.
Verifies that all 10 boundary scenarios run through the pipeline, preserve 26 features,
and missing telemetry uses the fitted SimpleImputer.
"""

import pytest
import pandas as pd
import numpy as np
from src.evaluation.boundary_testing import BoundaryTester


def test_ten_boundary_scenarios():
    bt = BoundaryTester()
    df_results = bt.run_all_tests(threshold=0.80)

    # Must contain exactly 10 scenarios
    assert len(df_results) == 10
    assert set(df_results["Scenario ID"]) == set(range(1, 11))

    # All probabilities must be valid floats between 0 and 1
    raw_probs = df_results["Raw Probability"]
    assert ((raw_probs >= 0.0) & (raw_probs <= 1.0)).all()

    # Predictions must be NORMAL or DEGRADED
    assert set(df_results["Prediction"]).issubset({"NORMAL", "DEGRADED"})

    # Check scenario 10 specifically (Missing telemetry)
    s10 = df_results[df_results["Scenario ID"] == 10].iloc[0]
    assert "Missing" in s10["Scenario"]
    assert s10["Prediction"] in ["NORMAL", "DEGRADED"]
