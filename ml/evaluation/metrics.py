import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List, Union
from sklearn.metrics import (
    precision_score, recall_score, f1_score,
    average_precision_score, roc_auc_score, confusion_matrix
)


def official_scania_cost(
    y_true_proximity_class: np.ndarray,
    y_pred_decision: np.ndarray
) -> Dict[str, float]:
    """
    Official SCANIA Component X Cost Function:
      y_true_proximity_class: integer array where:
        0 = Healthy (>48 steps to failure)
        1 = Class 1 (48-24 steps before failure)
        2 = Class 2 (24-12 steps before failure)
        3 = Class 3 (12-6 steps before failure)
        4 = Class 4 (6-0 steps before failure / catastrophic)
      
      y_pred_decision: binary maintenance decision (0 = Do Nothing, 1 = Trigger Maintenance)

      Cost Rules:
        - Actual Healthy (0) & Predict Maintenance (1) : Cost = 7   (Unnecessary inspection)
        - Actual Class 1 (1) & Predict Healthy (0)     : Cost = 200 (Missed 48-24h window)
        - Actual Class 2 (2) & Predict Healthy (0)     : Cost = 300 (Missed 24-12h window)
        - Actual Class 3 (3) & Predict Healthy (0)     : Cost = 400 (Missed 12-6h window)
        - Actual Class 4 (4) & Predict Healthy (0)     : Cost = 500 (Missed imminent failure)
        - Actual Failure (1-4) & Predict Maintenance (1): Cost = 0   (Timely intervention)
        - Actual Healthy (0) & Predict Healthy (0)     : Cost = 0   (Normal operation)
    """
    y_true = np.asarray(y_true_proximity_class, dtype=int)
    y_pred = np.asarray(y_pred_decision, dtype=int)

    # Cost vectors
    costs = np.zeros(len(y_true), dtype=float)

    # False Alarms on healthy trucks
    false_alarms = (y_true == 0) & (y_pred == 1)
    costs[false_alarms] = 7.0

    # Missed Failures by severity class
    costs[(y_true == 1) & (y_pred == 0)] = 200.0
    costs[(y_true == 2) & (y_pred == 0)] = 300.0
    costs[(y_true == 3) & (y_pred == 0)] = 400.0
    costs[(y_true == 4) & (y_pred == 0)] = 500.0

    total_cost = float(np.sum(costs))
    cost_per_sample = total_cost / max(1, len(y_true))

    return {
        "official_scania_total_cost": total_cost,
        "official_scania_cost_per_sample": cost_per_sample,
        "false_alarm_count": int(np.sum(false_alarms)),
        "missed_class_1_count": int(np.sum((y_true == 1) & (y_pred == 0))),
        "missed_class_2_count": int(np.sum((y_true == 2) & (y_pred == 0))),
        "missed_class_3_count": int(np.sum((y_true == 3) & (y_pred == 0))),
        "missed_class_4_count": int(np.sum((y_true == 4) & (y_pred == 0))),
        "timely_maintenance_count": int(np.sum((y_true >= 1) & (y_pred == 1))),
    }


def custom_normalized_cost(
    y_true_binary: np.ndarray,
    y_pred_binary: np.ndarray,
    c_fn: float = 500.0,
    c_fp: float = 10.0,
    c_tp: float = 10.0,
    c_tn: float = 0.0
) -> Dict[str, float]:
    """
    Simplified Custom Binary Cost Metric:
      - c_fn: penalty for missed failure (default 500.0)
      - c_fp: penalty for false alarm inspection (default 10.0)
      - c_tp: cost of scheduled workshop repair (default 10.0)
      - c_tn: normal operation cost (default 0.0)
    """
    tn, fp, fn, tp = confusion_matrix(y_true_binary, y_pred_binary, labels=[0, 1]).ravel()
    total_cost = (
        float(fn) * c_fn +
        float(fp) * c_fp +
        float(tp) * c_tp +
        float(tn) * c_tn
    )
    return {
        "custom_total_cost": float(total_cost),
        "custom_cost_per_sample": float(total_cost / max(1, len(y_true_binary))),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    }


def map_time_to_failure_to_proximity_classes(time_to_failure_array: np.ndarray) -> np.ndarray:
    """
    Maps continuous time-to-failure into SCANIA 5-class proximity bins:
      Class 0: Healthy (> 48 steps or healthy/censored truck with -1)
      Class 1: 48 >= delta_t > 24
      Class 2: 24 >= delta_t > 12
      Class 3: 12 >= delta_t > 6
      Class 4: 6 >= delta_t >= 0
    """
    ttf = np.asarray(time_to_failure_array, dtype=float)
    classes = np.zeros(len(ttf), dtype=int)
    
    classes[(ttf <= 48) & (ttf > 24)] = 1
    classes[(ttf <= 24) & (ttf > 12)] = 2
    classes[(ttf <= 12) & (ttf > 6)] = 3
    classes[(ttf <= 6) & (ttf >= 0)] = 4
    return classes


def evaluate_binary_predictions(
    y_true_binary: np.ndarray,
    y_proba: np.ndarray,
    threshold: float = 0.5,
    y_true_proximity_classes: Optional[np.ndarray] = None
) -> Dict[str, float]:
    """Comprehensive evaluation returning classification metrics, official Scania costs, and custom binary costs."""
    y_pred = (y_proba >= threshold).astype(int)
    
    pr_auc = float(average_precision_score(y_true_binary, y_proba)) if len(np.unique(y_true_binary)) > 1 else 0.0
    roc_auc = float(roc_auc_score(y_true_binary, y_proba)) if len(np.unique(y_true_binary)) > 1 else 0.5
    
    precision = float(precision_score(y_true_binary, y_pred, zero_division=0))
    recall = float(recall_score(y_true_binary, y_pred, zero_division=0))
    f1 = float(f1_score(y_true_binary, y_pred, zero_division=0))
    
    cm = confusion_matrix(y_true_binary, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    results = {
        "threshold": float(threshold),
        "pr_auc": pr_auc,
        "roc_auc": roc_auc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
    }

    # Custom normalized binary cost
    custom_cost_res = custom_normalized_cost(y_true_binary, y_pred)
    results.update(custom_cost_res)

    # Official Scania 5-class cost if proximity classes are available
    if y_true_proximity_classes is not None:
        official_res = official_scania_cost(y_true_proximity_classes, y_pred)
        results.update(official_res)
        
    return results


def run_threshold_sweep(
    y_true_binary: np.ndarray,
    y_proba: np.ndarray,
    y_true_proximity_classes: Optional[np.ndarray] = None,
    thresholds: Optional[List[float]] = None
) -> pd.DataFrame:
    """
    Sweeps a range of thresholds and returns a structured comparison DataFrame.
    """
    if thresholds is None:
        thresholds = [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]

    rows = []
    for t in thresholds:
        metrics = evaluate_binary_predictions(
            y_true_binary, y_proba, threshold=t, y_true_proximity_classes=y_true_proximity_classes
        )
        row = {
            "Threshold": t,
            "Precision": round(metrics["precision"], 4),
            "Recall": round(metrics["recall"], 4),
            "F1": round(metrics["f1"], 4),
            "TP": metrics["true_positives"],
            "FP": metrics["false_positives"],
            "FN": metrics["false_negatives"],
            "Custom Binary Cost ($)": metrics.get("custom_total_cost", 0.0),
        }
        if "official_scania_total_cost" in metrics:
            row["Official Scania Cost ($)"] = metrics["official_scania_total_cost"]
            row["False Alarms (Cost=7)"] = metrics["false_alarm_count"]
            row["Missed Failures (Cost=200-500)"] = (
                metrics["missed_class_1_count"] + metrics["missed_class_2_count"] + 
                metrics["missed_class_3_count"] + metrics["missed_class_4_count"]
            )
        rows.append(row)

    return pd.DataFrame(rows)
