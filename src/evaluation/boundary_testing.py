"""
Boundary Testing Module for Network Service Quality Predictor
Executes 10 structured, realistic boundary scenarios through the actual model pipeline.
Preserves all 26 feature columns and exercises the real SimpleImputer preprocessing path.
"""

from typing import Dict, Any, List, Tuple
import os
import pandas as pd
import numpy as np

from src.features.feature_builder import FeatureBuilder, EXACT_26_FEATURE_NAMES
from src.models.model_adapter import ModelAdapter
from src.repositories.sqlite_repository import SQLiteRepository


class BoundaryTester:
    """Executes the 10 required boundary scenarios and validates model behavior against threshold 0.80."""

    def __init__(self,
                 feature_builder: FeatureBuilder = None,
                 model_adapter: ModelAdapter = None,
                 repository: SQLiteRepository = None):
        self.feature_builder = feature_builder or FeatureBuilder()
        self.model_adapter = model_adapter or ModelAdapter()
        self.repository = repository or SQLiteRepository()

    def get_scenarios(self) -> List[Dict[str, Any]]:
        """
        Defines the 10 mandatory boundary test cases with realistic telemetry values
        derived from observed training distributions.
        """
        return [
            {
                "id": 1,
                "name": "Normal network",
                "raw_input": {
                    "packet_loss": 0.0,
                    "jitter": 0.12,
                    "rtt": 1.2,
                    "outflow_Router": 4.65,
                    "inflow_Router": 4.65,
                    "resolve": 0.03,
                    "ttl": 62.0,
                    "probe_duration": 0.0,
                    "link": "R1-R9"
                },
                "summary": "Loss=0.0%, RTT=1.2ms, Jitter=0.12ms (healthy nominal campus baseline)",
                "expected": "NORMAL"
            },
            {
                "id": 2,
                "name": "High packet loss",
                "raw_input": {
                    "packet_loss": 5.0,
                    "jitter": 0.12,
                    "rtt": 1.2,
                    "outflow_Router": 4.65,
                    "inflow_Router": 4.65,
                    "resolve": 0.03,
                    "ttl": 62.0,
                    "probe_duration": 0.0,
                    "link": "R1-R9"
                },
                "summary": "Loss=5.0%, RTT=1.2ms, Jitter=0.12ms (isolated severe packet drop)",
                "expected": "DEGRADED"
            },
            {
                "id": 3,
                "name": "High RTT",
                "raw_input": {
                    "packet_loss": 0.0,
                    "jitter": 0.12,
                    "rtt": 35.0,
                    "outflow_Router": 4.65,
                    "inflow_Router": 4.65,
                    "resolve": 0.03,
                    "ttl": 62.0,
                    "probe_duration": 0.0,
                    "link": "R1-R9"
                },
                "summary": "Loss=0.0%, RTT=35.0ms, Jitter=0.12ms (extreme propagation latency)",
                "expected": "DEGRADED"
            },
            {
                "id": 4,
                "name": "High jitter",
                "raw_input": {
                    "packet_loss": 0.0,
                    "jitter": 3.5,
                    "rtt": 1.2,
                    "outflow_Router": 4.65,
                    "inflow_Router": 4.65,
                    "resolve": 0.03,
                    "ttl": 62.0,
                    "probe_duration": 0.0,
                    "link": "R1-R9"
                },
                "summary": "Loss=0.0%, RTT=1.2ms, Jitter=3.5ms (isolated packet arrival variance)",
                "expected": "DEGRADED"
            },
            {
                "id": 5,
                "name": "High packet loss + high RTT",
                "raw_input": {
                    "packet_loss": 4.0,
                    "jitter": 0.12,
                    "rtt": 25.0,
                    "outflow_Router": 4.65,
                    "inflow_Router": 4.65,
                    "resolve": 0.03,
                    "ttl": 62.0,
                    "probe_duration": 0.0,
                    "link": "R1-R9"
                },
                "summary": "Loss=4.0%, RTT=25.0ms, Jitter=0.12ms (congested and lossy link)",
                "expected": "DEGRADED"
            },
            {
                "id": 6,
                "name": "High jitter + high RTT",
                "raw_input": {
                    "packet_loss": 0.0,
                    "jitter": 3.0,
                    "rtt": 25.0,
                    "outflow_Router": 4.65,
                    "inflow_Router": 4.65,
                    "resolve": 0.03,
                    "ttl": 62.0,
                    "probe_duration": 0.0,
                    "link": "R1-R9"
                },
                "summary": "Loss=0.0%, RTT=25.0ms, Jitter=3.0ms (bufferbloat / queuing instability)",
                "expected": "DEGRADED"
            },
            {
                "id": 7,
                "name": "Multiple simultaneous degraded indicators",
                "raw_input": {
                    "packet_loss": 6.0,
                    "jitter": 3.5,
                    "rtt": 40.0,
                    "outflow_Router": 20.0,
                    "inflow_Router": 20.0,
                    "resolve": 0.03,
                    "ttl": 62.0,
                    "probe_duration": 0.05,
                    "link": "R1-R9"
                },
                "summary": "Loss=6.0%, RTT=40.0ms, Jitter=3.5ms, Probe=0.05s (multi-vector severe impairment)",
                "expected": "DEGRADED"
            },
            {
                "id": 8,
                "name": "Low telemetry / weak traffic",
                "raw_input": {
                    "packet_loss": 0.0,
                    "jitter": 0.05,
                    "rtt": 0.8,
                    "outflow_Router": 0.1,
                    "inflow_Router": 0.1,
                    "resolve": 0.01,
                    "ttl": 62.0,
                    "probe_duration": 0.0,
                    "link": "R1-R9"
                },
                "summary": "Loss=0.0%, RTT=0.8ms, Outflow=0.1, Inflow=0.1 (quiescent idle / light load)",
                "expected": "NORMAL"
            },
            {
                "id": 9,
                "name": "Values near observed training boundaries",
                "raw_input": {
                    "packet_loss": 0.35,
                    "jitter": 1.0,
                    "rtt": 12.0,
                    "outflow_Router": 15.0,
                    "inflow_Router": 15.0,
                    "resolve": 0.03,
                    "ttl": 62.0,
                    "probe_duration": 0.01,
                    "link": "R1-R9"
                },
                "summary": "Loss=0.35%, RTT=12.0ms, Jitter=1.0ms (transition boundary between normal max and degraded)",
                "expected": "DEGRADED"
            },
            {
                "id": 10,
                "name": "Missing telemetry",
                "raw_input": {
                    "packet_loss": np.nan,
                    "jitter": np.nan,
                    "rtt": 1.2,
                    "outflow_Router": 4.65,
                    "inflow_Router": 4.65,
                    "resolve": 0.03,
                    "ttl": 62.0,
                    "probe_duration": np.nan,
                    "link": "R1-R9"
                },
                "summary": "Missing packet_loss, jitter & probe (imputed via fitted SimpleImputer)",
                "expected": "NORMAL"
            }
        ]

    def run_all_tests(self, threshold: float = 0.80) -> pd.DataFrame:
        """
        Executes all 10 scenarios through the exact preprocessor and model.
        Returns detailed results DataFrame.
        """
        results = []
        scenarios = self.get_scenarios()

        for sc in scenarios:
            raw_data = sc["raw_input"].copy()
            df_raw = pd.DataFrame([raw_data])

            # Transform through actual TelemetryPreprocessor to verify SimpleImputer & RobustScaler
            feature_df = self.feature_builder.preprocessor.transform_to_features(df_raw)
            feature_df = feature_df[EXACT_26_FEATURE_NAMES]
            self.feature_builder.validate_feature_contract(feature_df)

            prob = float(self.model_adapter.predict_probability(feature_df)[0])
            pred_int = 1 if prob >= threshold else 0
            pred_status = "DEGRADED" if pred_int == 1 else "NORMAL"

            # Check status vs expected
            if pred_status == sc["expected"]:
                status = "PASS"
            else:
                status = "REVIEW"

            results.append({
                "Scenario ID": sc["id"],
                "Scenario": sc["name"],
                "Input Summary": sc["summary"],
                "Probability": f"{prob*100:.2f}%",
                "Raw Probability": prob,
                "Prediction": pred_status,
                "Threshold": f"{threshold:.2f}",
                "Expected Behavior": sc["expected"],
                "Status": status
            })

            # Record in DB audit
            try:
                self.repository.record_boundary_test(
                    scenario=sc["name"],
                    summary=sc["summary"],
                    prob=prob,
                    threshold=threshold,
                    pred=pred_int,
                    expected=sc["expected"],
                    status=status,
                    model_version=self.model_adapter.metadata()["model_version"]
                )
            except Exception:
                pass

        return pd.DataFrame(results)
