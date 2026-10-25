"""Evaluation metrics for face recognition, on labelled test fixtures only.

Accuracy, precision, recall, False Acceptance Rate (FAR), False
Rejection Rate (FRR) and mean processing time. These numbers are only
meaningful on a real enrolled/unknown test set; synthetic-vector tests
in tests/ verify the maths, they do NOT measure real face accuracy.
"""
from __future__ import annotations
from typing import List

def evaluate(predicted: List[str], actual: List[str],
             positive: str = "present") -> dict:
    if len(predicted) != len(actual):
        raise ValueError("predicted and actual must have the same length.")
    tp = sum(1 for p, a in zip(predicted, actual) if p == positive and a == positive)
    fp = sum(1 for p, a in zip(predicted, actual) if p == positive and a != positive)
    tn = sum(1 for p, a in zip(predicted, actual) if p != positive and a != positive)
    fn = sum(1 for p, a in zip(predicted, actual) if p != positive and a == positive)
    total = max(len(actual), 1)
    accuracy = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    far = fp / (fp + tn) if (fp + tn) else 0.0
    frr = fn / (fn + tp) if (fn + tp) else 0.0
    return {"accuracy": round(accuracy, 4), "precision": round(precision, 4),
            "recall": round(recall, 4), "far": round(far, 4), "frr": round(frr, 4),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn}

def mean_processing_time(times_seconds: List[float]) -> float:
    if not times_seconds:
        return 0.0
    return sum(times_seconds) / len(times_seconds)
