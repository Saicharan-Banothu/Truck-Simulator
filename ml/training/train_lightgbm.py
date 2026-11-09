import sys
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

# Ensure root in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ml.data.dataset_loader import load_raw_dataset, get_active_data_dir, REAL_DATA_DIR, SYNTHETIC_DATA_DIR
from ml.preprocessing.transformers import CausalSequencePreprocessor
from ml.features.temporal_features import (
    generate_horizon_labels,
    build_temporal_features,
    validate_leakage_safeguards
)
from ml.models.lightgbm_baseline import create_lightgbm_model, get_feature_importances
from ml.evaluation.metrics import (
    official_scania_cost,
    custom_normalized_cost,
    evaluate_binary_predictions,
    map_time_to_failure_to_proximity_classes,
    run_threshold_sweep
)

ARTIFACTS_DIR = PROJECT_ROOT / "ml" / "artifacts"


def train_lightgbm_pipeline(
    data_dir: Path = DEFAULT_DATA_DIR,
    horizon: int = 48,
    scale_pos_weight: float = 6.0,
    artifacts_dir: Path = ARTIFACTS_DIR
) -> dict:
    """
    Executes the complete, leak-free LightGBM baseline training and evaluation pipeline:
      1. Load raw split data.
      2. Run leakage safeguards validation.
      3. Generate causal prediction horizon labels.
      4. Fit preprocessor ONLY on training readouts.
      5. Transform train/val/test data.
      6. Build causal temporal summary features.
      7. Train LightGBM model.
      8. Optimize decision threshold on Validation set using Scania Cost Matrix.
      9. Evaluate frozen optimal threshold on held-out Test set.
      10. Save all artifacts and metadata JSON.
    """
    start_time = time.time()
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("           LIGHTGBM BASELINE TRAINING & EVALUATION PIPELINE")
    print("=" * 80)

    # 1. Load data
    print("\n[Step 1/8] Loading dataset splits...")
    data = load_raw_dataset(data_dir)
    train_readouts = data["train_readouts"]
    train_tte = data["train_tte"]
    train_specs = data["train_specs"]

    val_readouts = data["val_readouts"]
    val_labels = data["val_labels"]
    val_specs = data["val_specs"]
    val_tte = data.get("val_tte", None)
    if val_tte is None:
        val_tte = pd.read_csv(data_dir / "validation_tte.csv") if (data_dir / "validation_tte.csv").exists() else train_tte

    test_readouts = data["test_readouts"]
    test_labels = data["test_labels"]
    test_specs = data["test_specs"]
    test_tte = data.get("test_tte", None)
    if test_tte is None:
        test_tte = pd.read_csv(data_dir / "test_tte.csv") if (data_dir / "test_tte.csv").exists() else train_tte

    # 2. Leakage safeguards
    print("\n[Step 2/8] Validating data leakage safeguards...")
    leakage_report = validate_leakage_safeguards(train_readouts, val_readouts, test_readouts)
    print(f"  - Vehicle Separation Across Splits : {'PASSED' if leakage_report['vehicle_separation_passed'] else 'FAILED'}")
    print(f"  - Causal Time Monotonicity         : {'PASSED' if leakage_report['causal_monotonicity_passed'] else 'FAILED'}")
    if not leakage_report["vehicle_separation_passed"]:
        raise ValueError("Data Leakage Detected: Vehicle IDs overlap across splits!")

    # 3. Generate causal labels
    print(f"\n[Step 3/8] Generating causal prediction horizon labels (Horizon = {horizon} timesteps)...")
    train_y_df = generate_horizon_labels(train_readouts, train_tte, horizon=horizon)
    val_y_df = generate_horizon_labels(val_readouts, val_tte, horizon=horizon)
    test_y_df = generate_horizon_labels(test_readouts, test_tte, horizon=horizon)

    y_train = train_y_df["label"].values
    y_val = val_y_df["label"].values
    y_test = test_y_df["label"].values

    print(f"  - Train Positive Label Rate : {y_train.sum():,d} / {len(y_train):,d} ({y_train.mean():.2%})")
    print(f"  - Val Positive Label Rate   : {y_val.sum():,d} / {len(y_val):,d} ({y_val.mean():.2%})")
    print(f"  - Test Positive Label Rate  : {y_test.sum():,d} / {len(y_test):,d} ({y_test.mean():.2%})")

    # 4. Preprocessing
    print("\n[Step 4/8] Fitting preprocessor strictly on Training data...")
    counter_cols = [c for c in train_readouts.columns if "counter" in c]
    hist_cols = [c for c in train_readouts.columns if "hist" in c]
    spec_cols = [c for c in train_specs.columns if c != "vehicle_id"]

    preprocessor = CausalSequencePreprocessor(
        counter_cols=counter_cols,
        hist_cols=hist_cols,
        spec_cols=spec_cols
    )
    preprocessor.fit(train_readouts, train_specs)

    print("  - Transforming train, val, and test splits with frozen training scaler...")
    train_pre = preprocessor.transform(train_readouts, train_specs)
    val_pre = preprocessor.transform(val_readouts, val_specs)
    test_pre = preprocessor.transform(test_readouts, test_specs)

    # 5. Temporal summary features
    print("\n[Step 5/8] Building causal temporal summary features...")
    transformed_num_cols = preprocessor.transformed_feature_names
    X_train_df, feature_names = build_temporal_features(train_pre, transformed_num_cols, spec_cols=spec_cols)
    X_val_df, _ = build_temporal_features(val_pre, transformed_num_cols, spec_cols=spec_cols)
    X_test_df, _ = build_temporal_features(test_pre, transformed_num_cols, spec_cols=spec_cols)

    # Align column sets (e.g. one-hot spec columns)
    for col in feature_names:
        if col not in X_val_df.columns:
            X_val_df[col] = 0
        if col not in X_test_df.columns:
            X_test_df[col] = 0

    X_train = X_train_df[feature_names].values
    X_val = X_val_df[feature_names].values
    X_test = X_test_df[feature_names].values

    print(f"  - Generated {len(feature_names)} engineered causal features.")

    # 6. Train LightGBM
    print("\n[Step 6/8] Training LightGBM Classifier...")
    model = create_lightgbm_model(
        n_estimators=180,
        learning_rate=0.04,
        max_depth=6,
        num_leaves=31,
        scale_pos_weight=scale_pos_weight
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[]
    )

    # 7. Evaluate and Optimize Threshold on Validation Set
    print("\n[Step 7/8] Optimizing Decision Threshold on Validation Set...")
    val_proba = model.predict_proba(X_val)[:, 1]
    val_ttf = val_y_df["time_to_failure"].values
    y_val_proximity = map_time_to_failure_to_proximity_classes(val_ttf)

    sweep_df = run_threshold_sweep(y_val, val_proba, y_true_proximity_classes=y_val_proximity)
    
    # Select threshold minimizing Official Scania Cost on validation
    best_row_idx = sweep_df["Official Scania Cost ($)"].idxmin()
    optimal_threshold = float(sweep_df.loc[best_row_idx, "Threshold"])

    val_full_metrics = evaluate_binary_predictions(
        y_val, val_proba, threshold=optimal_threshold, y_true_proximity_classes=y_val_proximity
    )

    print(f"  - Selected Optimal Threshold : {optimal_threshold:.4f}")
    print(f"  - Validation PR-AUC          : {val_full_metrics['pr_auc']:.4f}")
    print(f"  - Validation ROC-AUC         : {val_full_metrics['roc_auc']:.4f}")
    print(f"  - Validation F1-Score        : {val_full_metrics['f1']:.4f}")
    print(f"  - Validation Precision       : {val_full_metrics['precision']:.4f}")
    print(f"  - Validation Recall          : {val_full_metrics['recall']:.4f}")
    print(f"  - Validation False Negatives : {val_full_metrics['false_negatives']} (Missed Failures)")
    print(f"  - Validation False Positives : {val_full_metrics['false_positives']} (False Alarms)")
    print(f"  - Validation Official Cost   : ${val_full_metrics.get('official_scania_total_cost', 0):,.2f}")
    print(f"  - Validation Custom Cost     : ${val_full_metrics.get('custom_total_cost', 0):,.2f}")

    # 8. Evaluate on Held-Out Test Set (Exactly Once)
    print("\n[Step 8/8] Evaluating on HELD-OUT TEST SET with Frozen Optimal Threshold...")
    test_proba = model.predict_proba(X_test)[:, 1]
    test_ttf = test_y_df["time_to_failure"].values
    y_test_proximity = map_time_to_failure_to_proximity_classes(test_ttf)

    test_full_metrics = evaluate_binary_predictions(
        y_test, test_proba, threshold=optimal_threshold, y_true_proximity_classes=y_test_proximity
    )

    print(f"  - Test PR-AUC                : {test_full_metrics['pr_auc']:.4f}")
    print(f"  - Test ROC-AUC               : {test_full_metrics['roc_auc']:.4f}")
    print(f"  - Test F1-Score              : {test_full_metrics['f1']:.4f}")
    print(f"  - Test Precision             : {test_full_metrics['precision']:.4f}")
    print(f"  - Test Recall                : {test_full_metrics['recall']:.4f}")
    print(f"  - Test False Negatives       : {test_full_metrics['false_negatives']} (Missed Failures)")
    print(f"  - Test False Positives       : {test_full_metrics['false_positives']} (False Alarms)")
    print(f"  - Test Official Scania Cost  : ${test_full_metrics.get('official_scania_total_cost', 0):,.2f}")
    print(f"  - Test Custom Cost           : ${test_full_metrics.get('custom_total_cost', 0):,.2f}")

    # 9. Feature Importance
    df_importances = get_feature_importances(model, feature_names)
    print("\nTop 10 Most Important Features:")
    for _, row in df_importances.head(10).iterrows():
        print(f"  - {row['feature']:35s}: {row['importance']:5.0f} ({row['relative_importance']:.2%})")

    # 10. Save Artifacts
    print(f"\nSaving artifacts to '{artifacts_dir}'...")
    joblib.dump(model, artifacts_dir / "lightgbm_model.joblib")
    joblib.dump(preprocessor, artifacts_dir / "preprocessor.joblib")
    
    feature_config = {
        "feature_names": feature_names,
        "counter_cols": counter_cols,
        "hist_cols": hist_cols,
        "spec_cols": spec_cols,
        "transformed_num_cols": transformed_num_cols,
        "prediction_horizon": horizon
    }
    with open(artifacts_dir / "feature_config.json", "w") as f:
        json.dump(feature_config, f, indent=2)

    metadata = {
        "model_type": "LightGBM_Baseline",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prediction_horizon_steps": horizon,
        "optimal_threshold": optimal_threshold,
        "cost_matrix_weights": {
            "c_fn": cost_matrix.c_fn,
            "c_fp": cost_matrix.c_fp,
            "c_tp": cost_matrix.c_tp,
            "c_tn": cost_matrix.c_tn
        },
        "dataset_summary": {
            "train_rows": len(train_readouts),
            "val_rows": len(val_readouts),
            "test_rows": len(test_readouts),
            "train_vehicles": leakage_report["train_vehicles_count"],
            "val_vehicles": leakage_report["val_vehicles_count"],
            "test_vehicles": leakage_report["test_vehicles_count"],
        },
        "validation_metrics": val_full_metrics,
        "test_metrics": test_full_metrics,
        "top_features": df_importances.head(15).to_dict(orient="records"),
        "elapsed_training_seconds": round(time.time() - start_time, 2)
    }
    with open(artifacts_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("=" * 80)
    print("LIGHTGBM BASELINE TRAINING & ARTIFACT EXPORT COMPLETE")
    print("=" * 80)
    return metadata


if __name__ == "__main__":
    train_lightgbm_pipeline()
