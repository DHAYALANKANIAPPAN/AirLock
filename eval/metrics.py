"""Evaluation metrics calculation for Airlock and baseline defenses."""
from __future__ import annotations

from typing import Any, Dict, List


def calculate_confusion_matrix(predictions: List[str], ground_truth: List[str]) -> Dict[str, int]:
    """Compute basic binary/multi-class confusion counts.

    For security evaluation:
      Positive = Attack / Malicious injection
      Negative = Benign (both plain benign and tricky benign)
    """
    tp = sum(1 for p, g in zip(predictions, ground_truth) if p == "attack" and g == "attack")
    fp = sum(1 for p, g in zip(predictions, ground_truth) if p == "attack" and g != "attack")
    tn = sum(1 for p, g in zip(predictions, ground_truth) if p != "attack" and g != "attack")
    fn = sum(1 for p, g in zip(predictions, ground_truth) if p != "attack" and g == "attack")

    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn}


def calculate_metrics(predictions: List[str], ground_truth: List[str]) -> Dict[str, float]:
    """Calculate accuracy, precision, recall, F1, and False Positive Rate on tricky benign."""
    cm = calculate_confusion_matrix(predictions, ground_truth)
    tp, fp, tn, fn = cm["tp"], cm["fp"], cm["tn"], cm["fn"]

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / len(predictions) if predictions else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    bypass_rate = fn / (tp + fn) if (tp + fn) > 0 else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
        "attack_bypass_rate": round(bypass_rate, 4),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }
