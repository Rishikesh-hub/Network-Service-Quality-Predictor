"""
Integration Tests for FastAPI Backend Endpoints.
Covers health, model metadata, prediction, validation errors, unknown links, telemetry, alerts, and boundary tests.
"""

import pytest
from starlette.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert data["model_version"] == "mlp_ann_final"
    assert data["architecture"] == [128, 64]
    assert data["threshold"] == 0.80
    assert data["feature_count"] == 26
    assert data["prediction_type"] == "current_state"


def test_api_model_metadata():
    res = client.get("/api/model")
    assert res.status_code == 200
    data = res.json()
    assert data["model_type"] == "MLPClassifier"
    assert data["validation_f1"] == 0.9511
    assert data["final_test_f1"] == 0.9648
    assert data["final_test_far"] == 0.011805


def test_api_prediction_nominal():
    payload = {
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
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "NORMAL"
    assert data["prediction"] == 0
    assert data["probability"] < 0.80
    assert data["threshold"] == 0.80
    assert data["prediction_type"] == "current_state"
    assert len(data["contributors"]) > 0


def test_api_prediction_degraded():
    payload = {
        "packet_loss": 5.0,
        "jitter": 0.12,
        "rtt": 1.2,
        "outflow_Router": 4.65,
        "inflow_Router": 4.65,
        "resolve": 0.03,
        "ttl": 62.0,
        "probe_duration": 0.0,
        "link": "R1-R9"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "DEGRADED"
    assert data["prediction"] == 1
    assert data["probability"] >= 0.80


def test_api_prediction_invalid_input():
    # Missing required field 'rtt'
    payload = {
        "packet_loss": 0.0,
        "jitter": 0.12,
        "outflow_Router": 4.65,
        "inflow_Router": 4.65,
        "resolve": 0.03,
        "ttl": 62.0,
        "probe_duration": 0.0,
        "link": "R1-R9"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 422


def test_api_prediction_unknown_link():
    payload = {
        "packet_loss": 0.0,
        "jitter": 0.12,
        "rtt": 1.2,
        "outflow_Router": 4.65,
        "inflow_Router": 4.65,
        "resolve": 0.03,
        "ttl": 62.0,
        "probe_duration": 0.0,
        "link": "NON_EXISTENT_LINK"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 422
    assert "Unknown link" in res.json()["detail"]


def test_api_telemetry_endpoint():
    res = client.get("/api/telemetry?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "records" in data
    assert len(data["records"]) <= 10
    assert "summary_stats" in data
    assert "links" in data


def test_api_alerts_endpoint():
    res = client.get("/api/alerts")
    assert res.status_code == 200
    data = res.json()
    assert "alerts" in data
    assert "active_count" in data


def test_api_boundary_run_endpoint():
    res = client.post("/api/boundary-tests/run")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 10
    assert all("Scenario ID" in s for s in data)
    assert all("Probability" in s for s in data)
