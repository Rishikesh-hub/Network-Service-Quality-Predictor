"""
Tests for Model Adapter and Inference Semantics.
Validates loading trained MLPClassifier artifact, probability range, threshold 0.80 application, and metadata.
"""

import pytest
import numpy as np
import pandas as pd
from src.features.feature_builder import FeatureBuilder
from src.models.model_adapter import ModelAdapter


def test_model_loading_and_inference():
    ma = ModelAdapter()
    fb = FeatureBuilder()

    raw_sample = {
        "packet_loss": 0.0,
        "jitter": 1.0,
        "rtt": 20.0,
        "outflow_Router": 800.0,
        "inflow_Router": 780.0,
        "resolve": 1.0,
        "ttl": 60.0,
        "probe_duration": 0.1,
        "link": "R1-R2"
    }

    X = fb.build_from_raw_dict(raw_sample)
    probs = ma.predict_probability(X)
    assert len(probs) == 1
    assert 0.0 <= probs[0] <= 1.0

    preds = ma.predict(X, threshold=0.80)
    assert preds[0] in [0, 1]


def test_threshold_boundary():
    ma = ModelAdapter()
    fb = FeatureBuilder()
    X = fb.build_from_raw_dict({
        "packet_loss": 0.0, "jitter": 1.0, "rtt": 20.0, "outflow_Router": 800.0,
        "inflow_Router": 780.0, "resolve": 1.0, "ttl": 60.0, "probe_duration": 0.1, "link": "R1-R2"
    })

    # Test explicit custom thresholds
    # If prob < 0.80 -> 0
    p = ma.predict_probability(X)[0]
    expected_pred = 1 if p >= 0.80 else 0
    actual_pred = ma.predict(X, threshold=0.80)[0]
    assert actual_pred == expected_pred


def test_model_metadata():
    ma = ModelAdapter()
    meta = ma.metadata()
    assert meta["model_version"] == "mlp_ann_final"
    assert meta["architecture"] == [128, 64]
    assert meta["threshold"] == 0.80
    assert meta["prediction_type"] == "current_state"
    assert meta["feature_count"] == 26
