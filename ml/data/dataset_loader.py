import os
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REAL_DATA_DIR = PROJECT_ROOT / "data" / "real"
SYNTHETIC_DATA_DIR = PROJECT_ROOT / "data" / "synthetic"

EXPECTED_FILES = {
    "train_operational": "train_operational_readouts.csv",
    "train_tte": "train_tte.csv",
    "train_specs": "train_specifications.csv",
    "val_operational": "validation_operational_readouts.csv",
    "val_labels": "validation_labels.csv",
    "val_specs": "validation_specifications.csv",
    "test_operational": "test_operational_readouts.csv",
    "test_labels": "test_labels.csv",
    "test_specs": "test_specifications.csv",
}


def get_active_data_dir(prefer_real: bool = True) -> Tuple[Path, str]:
    """
    Returns the active data directory and a mode string ('real' or 'synthetic').
    If real data exists in data/real/, returns (REAL_DATA_DIR, 'real').
    Otherwise falls back to (SYNTHETIC_DATA_DIR, 'synthetic').
    """
    if prefer_real and is_dataset_present(REAL_DATA_DIR):
        return REAL_DATA_DIR, "real"
    if is_dataset_present(SYNTHETIC_DATA_DIR):
        return SYNTHETIC_DATA_DIR, "synthetic"
    return REAL_DATA_DIR, "missing"


def check_dataset_status(data_dir: Path) -> Dict[str, bool]:
    """Check existence of all expected dataset files in a directory."""
    status = {}
    for key, filename in EXPECTED_FILES.items():
        status[filename] = (data_dir / filename).exists()
    return status


def is_dataset_present(data_dir: Path) -> bool:
    """Returns True if minimum core files for train/val/test are present."""
    status = check_dataset_status(data_dir)
    core_files = [
        "train_operational_readouts.csv",
        "train_tte.csv"
    ]
    return all(status.get(f, False) for f in core_files)


def load_raw_dataset(data_dir: Optional[Path] = None) -> Tuple[Dict[str, pd.DataFrame], str]:
    """
    Loads raw CSV files into pandas DataFrames.
    Returns (data_dict, mode) where mode is 'real' or 'synthetic'.
    """
    if data_dir is None:
        data_dir, mode = get_active_data_dir()
    else:
        mode = "real" if "real" in str(data_dir) else "synthetic"

    status = check_dataset_status(data_dir)
    missing = [f for f, exists in status.items() if not exists]
    
    # Allow missing optional tte in validation/test if labels.csv exists
    critical_missing = [
        f for f in missing if f in [
            "train_operational_readouts.csv",
            "train_tte.csv",
            "train_specifications.csv",
            "validation_operational_readouts.csv",
            "test_operational_readouts.csv"
        ]
    ]

    if critical_missing:
        raise FileNotFoundError(
            f"Missing required dataset files in '{data_dir}':\n"
            + "\n".join(f" - {f}" for f in critical_missing)
            + f"\n\nMode: {mode.upper()}.\nPlease ensure files are placed in '{data_dir}'."
        )

    data = {
        "train_readouts": pd.read_csv(data_dir / EXPECTED_FILES["train_operational"]),
        "train_tte": pd.read_csv(data_dir / EXPECTED_FILES["train_tte"]),
        "train_specs": pd.read_csv(data_dir / EXPECTED_FILES["train_specs"]),
        "val_readouts": pd.read_csv(data_dir / EXPECTED_FILES["val_operational"]),
        "val_specs": pd.read_csv(data_dir / EXPECTED_FILES["val_specs"]),
        "test_readouts": pd.read_csv(data_dir / EXPECTED_FILES["test_operational"]),
        "test_specs": pd.read_csv(data_dir / EXPECTED_FILES["test_specs"]),
    }

    if (data_dir / EXPECTED_FILES["val_labels"]).exists():
        data["val_labels"] = pd.read_csv(data_dir / EXPECTED_FILES["val_labels"])
    if (data_dir / EXPECTED_FILES["test_labels"]).exists():
        data["test_labels"] = pd.read_csv(data_dir / EXPECTED_FILES["test_labels"])
    if (data_dir / "validation_tte.csv").exists():
        data["val_tte"] = pd.read_csv(data_dir / "validation_tte.csv")
    if (data_dir / "test_tte.csv").exists():
        data["test_tte"] = pd.read_csv(data_dir / "test_tte.csv")

    return data, mode
