import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ml.data.dataset_loader import load_raw_dataset, DEFAULT_DATA_DIR, check_dataset_status


def inspect_dataset(data_dir: Path = DEFAULT_DATA_DIR) -> str:
    """
    Performs comprehensive data inspection on the Scania Component X dataset.
    Generates and returns a detailed, formatted report.
    """
    report_lines = []
    def log(msg=""):
        report_lines.append(msg)

    log("=" * 80)
    log("       SCANIA COMPONENT X TELEMETRY DATASET INSPECTION REPORT")
    log("=" * 80)

    status = check_dataset_status(data_dir)
    log("\n[1] FILE INTEGRITY & PRESENCE:")
    for fname, exists in status.items():
        log(f"  - {fname:40s}: {'FOUND' if exists else 'MISSING'}")

    try:
        data = load_raw_dataset(data_dir)
    except Exception as e:
        log(f"\nError loading dataset: {e}")
        return "\n".join(report_lines)

    train_readouts = data["train_readouts"]
    train_tte = data["train_tte"]
    train_specs = data["train_specs"]

    val_readouts = data["val_readouts"]
    val_labels = data["val_labels"]

    test_readouts = data["test_readouts"]
    test_labels = data["test_labels"]

    log("\n[2] RECORD & VEHICLE VOLUME:")
    splits = [
        ("Train", train_readouts, train_tte),
        ("Validation", val_readouts, val_labels),
        ("Test", test_readouts, test_labels)
    ]
    total_rows = sum(len(df) for _, df, _ in splits)
    total_vehicles = sum(df["vehicle_id"].nunique() for _, df, _ in splits)

    for name, df_readouts, df_meta in splits:
        n_rows = len(df_readouts)
        n_veh = df_readouts["vehicle_id"].nunique()
        log(f"  - {name:12s}: {n_rows:8,d} telemetry rows | {n_veh:5,d} distinct vehicles")
    log(f"  - Total Fleet : {total_rows:8,d} telemetry rows | {total_vehicles:5,d} distinct vehicles")

    log("\n[3] SCHEMA & FEATURE TYPES (Train Readouts):")
    feature_cols = [c for c in train_readouts.columns if c not in ["vehicle_id", "time_step"]]
    counter_cols = [c for c in feature_cols if "counter" in c]
    hist_cols = [c for c in feature_cols if "hist" in c]
    other_cols = [c for c in feature_cols if c not in counter_cols and c not in hist_cols]

    log(f"  - Total Features: {len(feature_cols)} (excluding identifiers)")
    log(f"    * Operational Counters: {len(counter_cols)} ({', '.join(counter_cols[:4])}...)")
    log(f"    * Histogram Bins      : {len(hist_cols)} ({', '.join(hist_cols[:4])}...)")
    if other_cols:
        log(f"    * Other Numeric/State : {len(other_cols)} ({', '.join(other_cols)})")

    spec_cols = [c for c in train_specs.columns if c != "vehicle_id"]
    log(f"  - Specification Features : {len(spec_cols)} ({', '.join(spec_cols)})")

    log("\n[4] DATA QUALITY & MISSING VALUES:")
    missing_train = train_readouts.isnull().sum()
    total_missing = missing_train.sum()
    log(f"  - Missing Values in Train Readouts: {total_missing} ({total_missing / (len(train_readouts) * len(train_readouts.columns)):.4%})")
    
    dup_keys = train_readouts.duplicated(subset=["vehicle_id", "time_step"]).sum()
    log(f"  - Duplicate (vehicle_id, time_step) pairs: {dup_keys}")

    log("\n[5] TEMPORAL SEQUENCE LENGTHS & HORIZONS:")
    seq_lengths = train_readouts.groupby("vehicle_id")["time_step"].count()
    min_t = train_readouts["time_step"].min()
    max_t = train_readouts["time_step"].max()
    log(f"  - Time Step Range    : min = {min_t}, max = {max_t}")
    log(f"  - Sequence Length    : min = {seq_lengths.min()}, max = {seq_lengths.max()}, "
        f"mean = {seq_lengths.mean():.1f}, median = {seq_lengths.median():.1f}")

    log("\n[6] CLASS DISTRIBUTION & IMBALANCE:")
    train_repaired = train_tte["repaired"].sum() if "repaired" in train_tte.columns else 0
    train_total = len(train_tte)
    log(f"  - Train Vehicles Repaired (Failures): {train_repaired} / {train_total} ({train_repaired/train_total:.2%})")
    log(f"  - Train Vehicles Healthy (Censored) : {train_total - train_repaired} / {train_total} ({(train_total - train_repaired)/train_total:.2%})")

    if "class_label" in val_labels.columns:
        val_pos = val_labels["class_label"].sum()
        log(f"  - Val Vehicles Repaired (Failures)  : {val_pos} / {len(val_labels)} ({val_pos/len(val_labels):.2%})")
    if "class_label" in test_labels.columns:
        test_pos = test_labels["class_label"].sum()
        log(f"  - Test Vehicles Repaired (Failures) : {test_pos} / {len(test_labels)} ({test_pos/len(test_labels):.2%})")

    log("\n[7] TELEMETRY MONOTONICITY ANALYSIS:")
    sorted_df = train_readouts.sort_values(["vehicle_id", "time_step"])
    for col in counter_cols:
        diffs = sorted_df.groupby("vehicle_id")[col].diff().dropna()
        active = diffs[diffs != 0]
        mono_pct = (active > 0).mean() if len(active) > 0 else 1.0
        log(f"  - {col:15s}: Monotonic Increase Rate = {mono_pct:.2%}")

    log("=" * 80)
    report_text = "\n".join(report_lines)
    print(report_text)
    return report_text


if __name__ == "__main__":
    inspect_dataset()
