import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ml.data.dataset_loader import load_raw_dataset, get_active_data_dir, REAL_DATA_DIR, SYNTHETIC_DATA_DIR
from ml.preprocessing.transformers import CausalSequencePreprocessor
from ml.features.temporal_features import (
    generate_horizon_labels,
    build_temporal_features,
)
from ml.models.lightgbm_baseline import create_lightgbm_model
from ml.evaluation.metrics import (
    run_threshold_sweep,
    map_time_to_failure_to_proximity_classes,
    official_scania_cost,
    custom_normalized_cost
)


def perform_validation_threshold_analysis(horizon: int = 48) -> pd.DataFrame:
    """
    Trains LightGBM on training split, calculates validation probabilities,
    and runs comprehensive threshold sweeps across both Official Scania 5-Class Cost
    and Custom Normalized Binary Cost.
    """
    data_dir, mode = get_active_data_dir()
    print(f"Loading data from '{data_dir}' (Mode: {mode.upper()})...")
    
    data, _ = load_raw_dataset(data_dir)
    train_readouts = data["train_readouts"]
    train_tte = data["train_tte"]
    train_specs = data["train_specs"]

    val_readouts = data["val_readouts"]
    val_specs = data["val_specs"]
    val_tte = data.get("val_tte", None)
    if val_tte is None:
        val_tte = pd.read_csv(data_dir / "validation_tte.csv")

    # Labels
    train_y_df = generate_horizon_labels(train_readouts, train_tte, horizon=horizon)
    val_y_df = generate_horizon_labels(val_readouts, val_tte, horizon=horizon)

    y_train = train_y_df["label"].values
    y_val = val_y_df["label"].values
    val_ttf = val_y_df["time_to_failure"].values
    y_val_proximity = map_time_to_failure_to_proximity_classes(val_ttf)

    # Preprocess
    preprocessor = CausalSequencePreprocessor()
    preprocessor.fit(train_readouts, train_specs)

    train_pre = preprocessor.transform(train_readouts, train_specs)
    val_pre = preprocessor.transform(val_readouts, val_specs)

    X_train_df, feature_names = build_temporal_features(train_pre, preprocessor.transformed_feature_names)
    X_val_df, _ = build_temporal_features(val_pre, preprocessor.transformed_feature_names)

    for c in feature_names:
        if c not in X_val_df.columns:
            X_val_df[c] = 0

    X_train = X_train_df[feature_names].values
    X_val = X_val_df[feature_names].values

    # Train LightGBM
    model = create_lightgbm_model(n_estimators=180, learning_rate=0.04, scale_pos_weight=6.0)
    model.fit(X_train, y_train)

    val_proba = model.predict_proba(X_val)[:, 1]

    # Threshold sweep
    thresholds = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80]
    sweep_df = run_threshold_sweep(
        y_true_binary=y_val,
        y_proba=val_proba,
        y_true_proximity_classes=y_val_proximity,
        thresholds=thresholds
    )

    print("\n" + "=" * 105)
    print("                      VALIDATION THRESHOLD SENSITIVITY & COST ANALYSIS TABLE")
    print("=" * 105)
    print(sweep_df.to_string(index=False))
    print("=" * 105)

    return sweep_df


if __name__ == "__main__":
    perform_validation_threshold_analysis()
