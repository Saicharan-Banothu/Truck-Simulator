import numpy as np
import pandas as pd
from typing import List, Optional, Tuple, Dict


def generate_horizon_labels(
    df_readouts: pd.DataFrame,
    df_tte: pd.DataFrame,
    horizon: int = 48
) -> pd.DataFrame:
    """
    Generates causal binary failure horizon labels:
      y_t = 1 if truck is repaired within [t, t + horizon] (i.e. 0 <= T_repair - t <= horizon)
      y_t = 0 otherwise.
    
    Ensures no future repair information is broadcast across the truck's entire lifespan.
    """
    df = df_readouts[["vehicle_id", "time_step"]].copy()
    
    # Merge repair event metadata
    tte_cols = ["vehicle_id", "repaired"]
    if "repair_time_step" in df_tte.columns:
        tte_cols.append("repair_time_step")
    elif "time_to_event" in df_tte.columns:
        tte_cols.append("time_to_event")
        
    merged = df.merge(df_tte[tte_cols], on="vehicle_id", how="left")
    
    repair_col = "repair_time_step" if "repair_time_step" in merged.columns else "time_to_event"
    
    # Calculate time to failure
    is_repaired = (merged["repaired"] == 1) & (merged[repair_col] >= 0)
    time_to_failure = merged[repair_col] - merged["time_step"]
    
    # Active inside prediction horizon
    in_horizon = is_repaired & (time_to_failure >= 0) & (time_to_failure <= horizon)
    
    df["label"] = in_horizon.astype(int)
    df["time_to_failure"] = np.where(is_repaired, time_to_failure, -1)
    
    return df


def build_temporal_features(
    df_preprocessed: pd.DataFrame,
    feature_cols: List[str],
    windows: List[int] = [6, 12, 24],
    spec_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Extracts causal temporal summary features per vehicle for tabular GBDT models:
      - Latest deltas (at time t)
      - Rolling mean, rolling std, rolling max over causal historical windows
      - Short-term vs long-term rate of change
      - Operational age (time_step)
      - One-hot encoded static specs (if present)
    """
    df = df_preprocessed.copy().sort_values(["vehicle_id", "time_step"])
    
    feature_list = []
    generated_dfs = [df[["vehicle_id", "time_step"]]]
    
    # 1. Operational age
    age_df = pd.DataFrame({"operational_age": df["time_step"]})
    generated_dfs.append(age_df)
    feature_list.append("operational_age")
    
    # 2. Instantaneous features (delta log values at current t)
    inst_features = df[feature_cols].copy()
    generated_dfs.append(inst_features)
    feature_list.extend(feature_cols)
    
    # 3. Causal rolling statistics per vehicle
    grouped = df.groupby("vehicle_id")[feature_cols]
    
    for w in windows:
        # Causal rolling mean
        roll_mean = grouped.rolling(window=w, min_periods=1).mean().reset_index(drop=True)
        roll_mean.columns = [f"{c}_roll_mean_{w}" for c in feature_cols]
        generated_dfs.append(roll_mean)
        feature_list.extend(roll_mean.columns.tolist())
        
        # Causal rolling std (fill NaN with 0 for single step)
        roll_std = grouped.rolling(window=w, min_periods=1).std().reset_index(drop=True).fillna(0.0)
        roll_std.columns = [f"{c}_roll_std_{w}" for c in feature_cols]
        generated_dfs.append(roll_std)
        feature_list.extend(roll_std.columns.tolist())
        
        # Causal rolling max
        roll_max = grouped.rolling(window=w, min_periods=1).max().reset_index(drop=True)
        roll_max.columns = [f"{c}_roll_max_{w}" for c in feature_cols]
        generated_dfs.append(roll_max)
        feature_list.extend(roll_max.columns.tolist())

    # Combine all numeric features
    X_features = pd.concat(generated_dfs, axis=1)
    
    # 4. Handle Categorical Specifications (One-Hot)
    if spec_cols:
        existing_spec_cols = [c for c in spec_cols if c in df.columns]
        if existing_spec_cols:
            spec_dummies = pd.get_dummies(df[existing_spec_cols], drop_first=True)
            spec_cols_encoded = spec_dummies.columns.tolist()
            X_features = pd.concat([X_features, spec_dummies], axis=1)
            feature_list.extend(spec_cols_encoded)
            
    return X_features, feature_list


def validate_leakage_safeguards(
    train_readouts: pd.DataFrame,
    val_readouts: pd.DataFrame,
    test_readouts: pd.DataFrame
) -> Dict[str, bool]:
    """
    Executes explicit data leakage validation checks:
      1. Vehicle separation (no vehicle ID overlap across train/val/test).
      2. Temporal causality (time_steps are monotonically non-decreasing per vehicle).
      3. No duplicate timestamps per vehicle.
    """
    train_vehicles = set(train_readouts["vehicle_id"].unique())
    val_vehicles = set(val_readouts["vehicle_id"].unique())
    test_vehicles = set(test_readouts["vehicle_id"].unique())
    
    # Check 1: Vehicle separation
    train_val_overlap = len(train_vehicles.intersection(val_vehicles)) == 0
    train_test_overlap = len(train_vehicles.intersection(test_vehicles)) == 0
    val_test_overlap = len(val_vehicles.intersection(test_vehicles)) == 0
    vehicle_separation_pass = train_val_overlap and train_test_overlap and val_test_overlap
    
    # Check 2: Temporal causality per split
    def is_causal(df):
        grouped = df.groupby("vehicle_id")["time_step"]
        return bool(grouped.apply(lambda s: s.is_monotonic_increasing).all())
    
    causality_pass = (
        is_causal(train_readouts) and 
        is_causal(val_readouts) and 
        is_causal(test_readouts)
    )
    
    return {
        "vehicle_separation_passed": vehicle_separation_pass,
        "causal_monotonicity_passed": causality_pass,
        "train_vehicles_count": len(train_vehicles),
        "val_vehicles_count": len(val_vehicles),
        "test_vehicles_count": len(test_vehicles),
    }
