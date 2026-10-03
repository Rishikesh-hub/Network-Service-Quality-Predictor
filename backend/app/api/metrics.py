"""
Evaluation metrics endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/metrics")
def get_evaluation_metrics():
    return {
        "official_threshold": 0.80,
        "prediction_type": "current_state",
        "validation": {
            "threshold": 0.80,
            "f1": 0.9511,
            "false_alert_rate": 0.010488,
            "precision": 0.931389,
            "recall": 0.971602
        },
        "test": {
            "threshold": 0.80,
            "f1": 0.9648,
            "false_alert_rate": 0.011805,
            "precision": 0.9385,
            "recall": 0.9928,
            "default_threshold_050": {
                "f1": 0.9596,
                "false_alert_rate": 0.019165
            }
        },
        "benchmarks": [
            {
                "model": "Logistic Regression Baseline",
                "precision": "94.21%",
                "recall": "98.89%",
                "f1": "96.49%",
                "far": "2.03%",
                "threshold": 0.50
            },
            {
                "model": "Random Forest Benchmark",
                "precision": "99.81%",
                "recall": "91.89%",
                "f1": "95.69%",
                "far": "0.06%",
                "threshold": 0.50
            },
            {
                "model": "MLP / ANN (Default Threshold)",
                "precision": "92.05%",
                "recall": "97.45%",
                "f1": "95.96%",
                "far": "1.92%",
                "threshold": 0.50
            },
            {
                "model": "MLP / ANN (Tuned Optimal)",
                "precision": "93.14%",
                "recall": "97.16%",
                "f1": "96.48%",
                "far": "1.18%",
                "threshold": 0.80
            }
        ],
        "threshold_curve": [
            {"threshold": 0.20, "f1": 0.9286, "far": 0.0198},
            {"threshold": 0.30, "f1": 0.9327, "far": 0.0180},
            {"threshold": 0.40, "f1": 0.9358, "far": 0.0168},
            {"threshold": 0.50, "f1": 0.9400, "far": 0.0152},
            {"threshold": 0.60, "f1": 0.9431, "far": 0.0138},
            {"threshold": 0.70, "f1": 0.9463, "far": 0.0125},
            {"threshold": 0.80, "f1": 0.9511, "far": 0.0105}
        ]
    }
