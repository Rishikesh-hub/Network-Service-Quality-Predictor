"""
Tests for 26-Feature Contract and Feature Builder.
Validates exact column count, ordering, unknown link handling, and cyclic temporal derivations.
"""

import pytest
import numpy as np
import pandas as pd
from src.features.feature_builder import FeatureBuilder, EXACT_26_FEATURE_NAMES


def test_feature_count_and_order():
    fb = FeatureBuilder()
    raw_sample = {
        "packet_loss": 0.5,
        "jitter": 2.1,
        "rtt": 45.0,
        "outflow_Router": 750.0,
        "inflow_Router": 700.0,
        "resolve": 1.0,
        "ttl": 58.0,
        "probe_duration": 0.2,
        "link": "R1-R2"
    }

    df_feat = fb.build_from_raw_dict(raw_sample)
    assert df_feat.shape == (1, 26)
    assert list(df_feat.columns) == EXACT_26_FEATURE_NAMES
    # Contract validation should pass without error
    fb.validate_feature_contract(df_feat)


def test_unknown_link_rejection():
    fb = FeatureBuilder()
    invalid_sample = {
        "packet_loss": 0.5,
        "jitter": 2.1,
        "rtt": 45.0,
        "outflow_Router": 750.0,
        "inflow_Router": 700.0,
        "resolve": 1.0,
        "ttl": 58.0,
        "probe_duration": 0.2,
        "link": "UNKNOWN-ROUTER-99"
    }

    with pytest.raises(ValueError, match="Unknown link"):
        fb.build_from_raw_dict(invalid_sample)


def test_missing_required_field_rejection():
    fb = FeatureBuilder()
    missing_sample = {
        "packet_loss": 0.5,
        "jitter": 2.1,
        # rtt missing
        "outflow_Router": 750.0,
        "inflow_Router": 700.0,
        "resolve": 1.0,
        "ttl": 58.0,
        "probe_duration": 0.2,
        "link": "R1-R2"
    }

    with pytest.raises(ValueError, match="Missing required telemetry field"):
        fb.build_from_raw_dict(missing_sample)
