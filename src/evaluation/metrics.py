"""
Evaluation Metrics Module for Network Service Quality Predictor
Computes precision, recall, F1, False Alert Rate (FAR), and confusion matrix.
"""

from typing import Dict, Any, Tuple
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix


def calculate_far(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, int, int, int, int]:
    """
    Computes False Alert Rate (FAR) = FP / (FP + TN)
    Returns: (far, tn, fp, fn, tp)
    """
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    far = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    return far, int(tn), int(fp), int(fn), int(tp)


def evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, Any]:
    """
    Calculates comprehensive model evaluation metrics.
    """
    far, tn, fp, fn, tp = calculate_far(y_true, y_pred)
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    acc = float(accuracy_score(y_true, y_pred))

    metrics = {
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "false_alert_rate": far,
        "accuracy": acc,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "confusion_matrix": [[tn, fp], [fn, tp]]
    }
    return metrics
