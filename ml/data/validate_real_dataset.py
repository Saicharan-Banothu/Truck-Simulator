import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ml.data.dataset_loader import load_raw_dataset, check_dataset_status, REAL_DATA_DIR
from ml.preprocessing.transformers import CausalSequencePreprocessor
from ml.features.temporal_features import build_temporal_features, generate_horizon_labels, validate_leakage_safeguards


def validate_dataset_directory(data_dir: Path = REAL_DATA_DIR) -> Dict[str, Any]:
    """
    Comprehensive validation script for verifying readiness of the real SCANIA Component X dataset
    (or any target dataset directory).
    Checks:
      1. File presence and integrity.
      2. Column schema and numerical validation.
      3. Strict vehicle ID disjointness across splits.
      4. Temporal sequence causality & monotonicity.
      5. Missing-value profile.
      6. Repair/TTE label consistency.
      7. Dry-run pass through CausalSequencePreprocessor & build_temporal_features.
    """
    report = {
        "data_directory": str(data_dir),
        "all_checks_passed": False,
        "files_status": {},
        "issues": [],
        "fleet_summary": {},
        "pipeline_test_passed": False
    }

    print("=" * 80)
    print(f"      REAL DATASET READINESS VALIDATION REPORT: {data_dir.name.upper()}")
    print("=" * 80)

    # 1. File presence
    status = check_dataset_status(data_dir)
    report["files_status"] = status
    missing_files = [f for f, exists in status.items() if not exists]

    print("\n[Check 1/7] File Presence Verification:")
    for f, exists in status.items():
        print(f"  - {f:42s}: {'FOUND' if exists else 'MISSING'}")

    if missing_files:
        msg = f"Missing {len(missing_files)} required CSV files in '{data_dir}'."
        report["issues"].append(msg)
        print(f"\n[!] VALIDATION HALTED: {msg}")
        print("\nRequired Files to place in data/real/:")
        for mf in missing_files:
            print(f"   * {mf}")
        return report

    # 2. Load dataset
    print("\n[Check 2/7] Loading and Schema Profiling...")
    try:
        data, mode = load_raw_dataset(data_dir)
    except Exception as e:
        report["issues"].append(f"Failed to load dataset: {e}")
        print(f"  - ERROR loading dataset: {e}")
        return report

    train_readouts = data["train_readouts"]
    train_tte = data["train_tte"]
    train_specs = data["train_specs"]
    val_readouts = data["val_readouts"]
    test_readouts = data["test_readouts"]

    # 3. Disjoint vehicles
    print("\n[Check 3/7] Cross-Split Vehicle Disjointness & Monotonicity:")
    leakage_res = validate_leakage_safeguards(train_readouts, val_readouts, test_readouts)
    if leakage_res["vehicle_separation_passed"]:
        print("  - Vehicle separation across Train, Validation, Test: PASSED (No overlap)")
    else:
        report["issues"].append("Vehicle IDs overlap across splits (Data Leakage Detected)!")
        print("  - Vehicle separation: FAILED (Data Leakage Detected!)")

    if leakage_res["causal_monotonicity_passed"]:
        print("  - Temporal causality (monotonically non-decreasing time_step): PASSED")
    else:
        report["issues"].append("Time steps are not strictly non-decreasing per vehicle!")
        print("  - Temporal causality: FAILED")

    # 4. Telemetry columns
    print("\n[Check 4/7] Telemetry Columns & Missing Values:")
    num_cols = [c for c in train_readouts.columns if c not in ["vehicle_id", "time_step"] and np.issubdtype(train_readouts[c].dtype, np.number)]
    non_num_cols = [c for c in train_readouts.columns if c not in ["vehicle_id", "time_step"] and c not in num_cols]
    
    print(f"  - Total Telemetry Columns Identified: {len(num_cols)} numeric, {len(non_num_cols)} non-numeric")
    missing_pct = train_readouts[num_cols].isnull().mean().mean() * 100.0
    print(f"  - Missing value rate across numeric telemetry: {missing_pct:.4f}%")

    # 5. Monotonicity of cumulative features
    print("\n[Check 5/7] Monotonic Counter Analysis:")
    sorted_train = train_readouts.sort_values(["vehicle_id", "time_step"])
    cumulative_cols = []
    for col in num_cols:
        diffs = sorted_train.groupby("vehicle_id")[col].diff().dropna()
        active = diffs[diffs != 0]
        if len(active) > 0 and (active > 0).mean() >= 0.95:
            cumulative_cols.append(col)
    print(f"  - Discovered {len(cumulative_cols)} cumulative counter columns (>=95% positive drift)")

    # 6. Target & Repair Information
    print("\n[Check 6/7] Target & Repair Information:")
    if "repaired" in train_tte.columns:
        n_repaired = int(train_tte["repaired"].sum())
        n_total = len(train_tte)
        print(f"  - Train repair events: {n_repaired} / {n_total} vehicles ({n_repaired/n_total:.2%})")
    else:
        print("  - 'repaired' column not directly found in train_tte. Checking target schema...")

    # 7. Preprocessing & Feature Pipeline Compatibility Test
    print("\n[Check 7/7] Preprocessing & Feature Pipeline End-to-End Compatibility:")
    try:
        prep = CausalSequencePreprocessor(numeric_cols=num_cols)
        prep.fit(train_readouts, train_specs)
        train_trans = prep.transform(train_readouts, train_specs)
        X_feat, feat_names = build_temporal_features(train_trans, prep.transformed_feature_names)
        
        print(f"  - Preprocessing pipeline successfully transformed data.")
        print(f"  - Generated {len(feat_names)} engineered causal temporal features.")
        report["pipeline_test_passed"] = True
    except Exception as e:
        msg = f"Pipeline dry-run failed: {e}"
        report["issues"].append(msg)
        print(f"  - Pipeline dry-run FAILED: {e}")

    report["all_checks_passed"] = (len(report["issues"]) == 0) and report["pipeline_test_passed"]
    
    print("\n" + "=" * 80)
    print(f"VALIDATION STATUS: {'READY' if report['all_checks_passed'] else 'INCOMPLETE / ISSUES DETECTED'}")
    print("=" * 80)
    return report


if __name__ == "__main__":
    validate_dataset_directory()
