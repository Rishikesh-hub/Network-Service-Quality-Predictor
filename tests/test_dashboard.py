"""
Tests for Dashboard and Service Layer Integration.
Verifies service invocation, component compatibility, and simulation data loading.
"""

import pytest
import os
import pandas as pd
from src.services.prediction_service import PredictionService
from src.data.data_adapter import DataAdapter


def test_prediction_service_single_record():
    service = PredictionService()
    sample = {
        "packet_loss": 0.0,
        "jitter": 0.12,
        "rtt": 1.2,
        "outflow_Router": 4.65,
        "inflow_Router": 4.65,
        "resolve": 0.03,
        "ttl": 62.0,
        "probe_duration": 0.0,
        "link": "R1-R9"
    }

    res = service.predict_single(sample)
    assert "probability" in res
    assert 0.0 <= res["probability"] <= 1.0
    assert res["status"] in ["NORMAL", "DEGRADED"]
    assert res["threshold"] == 0.80
    assert res["prediction_type"] == "current_state"
    assert len(res["contributors"]) > 0


def test_prediction_service_batch():
    service = PredictionService()
    sample_df = pd.DataFrame([
        {
            "packet_loss": 0.0, "jitter": 0.12, "rtt": 1.2, "outflow_Router": 4.65,
            "inflow_Router": 4.65, "resolve": 0.03, "ttl": 62.0, "probe_duration": 0.0, "link": "R1-R9"
        },
        {
            "packet_loss": 5.0, "jitter": 2.5, "rtt": 35.0, "outflow_Router": 4.65,
            "inflow_Router": 4.65, "resolve": 0.03, "ttl": 62.0, "probe_duration": 0.0, "link": "R1-R9"
        }
    ])

    batch_res = service.predict_batch(sample_df)
    assert len(batch_res) == 2
    assert "probability" in batch_res.columns
    assert "prediction" in batch_res.columns
    assert "status" in batch_res.columns


def test_dashboard_file_exists():
    assert os.path.exists("dashboard.py")
