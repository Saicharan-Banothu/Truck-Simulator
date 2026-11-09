import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import json
import joblib

from ml.data.dataset_loader import load_raw_dataset, get_active_data_dir, REAL_DATA_DIR, SYNTHETIC_DATA_DIR
from ml.preprocessing.transformers import CausalDeltaLogTransformer, CausalSequencePreprocessor
from ml.features.temporal_features import (
    generate_horizon_labels,
    build_temporal_features,
    validate_leakage_safeguards
)
from ml.evaluation.metrics import (
    official_scania_cost,
    custom_normalized_cost,
    evaluate_binary_predictions,
    map_time_to_failure_to_proximity_classes
)
from ml.inference.predictor import TruckFailurePredictor


def test_causal_delta_log_transformer():
    """Test first-order difference and signed log transform."""
    df = pd.DataFrame({
        "vehicle_id": ["TRUCK_1", "TRUCK_1", "TRUCK_1"],
        "time_step": [0, 1, 2],
        "counter_01": [100.0, 150.0, 175.0]
    })
    trans = CausalDeltaLogTransformer(numeric_cols=["counter_01"])
    res = trans.transform(df)

    assert "counter_01_delta_log" in res.columns
    # delta_0 = 0 -> log1p(0) = 0
    # delta_1 = 50 -> log1p(50) = ln(51) ~ 3.9318
    # delta_2 = 25 -> log1p(25) = ln(26) ~ 3.2581
    assert np.isclose(res["counter_01_delta_log"].iloc[0], 0.0)
    assert np.isclose(res["counter_01_delta_log"].iloc[1], np.log1p(50.0))
    assert np.isclose(res["counter_01_delta_log"].iloc[2], np.log1p(25.0))


def test_causal_sequence_preprocessor_no_future_leakage():
    """Test that preprocessor fits on train and transforms validation without leakage."""
    train_df = pd.DataFrame({
        "vehicle_id": ["T1", "T1", "T2", "T2"],
        "time_step": [0, 1, 0, 1],
        "counter_01": [10.0, 20.0, 30.0, 50.0],
        "hist_01": [5.0, 5.0, 10.0, 10.0]
    })
    val_df = pd.DataFrame({
        "vehicle_id": ["T3", "T3"],
        "time_step": [0, 1],
        "counter_01": [100.0, 200.0],
        "hist_01": [20.0, 20.0]
    })
    prep = CausalSequencePreprocessor(counter_cols=["counter_01"], hist_cols=["hist_01"])
    prep.fit(train_df)
    
    assert prep.is_fitted
    val_trans = prep.transform(val_df)
    assert len(val_trans) == 2
    assert "counter_01_delta_log" in val_trans.columns


def test_label_generation_horizon():
    """Test that failure labels are strictly bounded inside [T_fail - horizon, T_fail]."""
    df_readouts = pd.DataFrame({
        "vehicle_id": ["T1"] * 6,
        "time_step": [0, 10, 20, 50, 60, 100]
    })
    # T1 fails at time_step 60 with horizon 48
    # Horizon window = [60 - 48, 60] = [12, 60]
    # time_step 0 -> outside (0)
    # time_step 10 -> outside (0)
    # time_step 20 -> inside (1)
    # time_step 50 -> inside (1)
    # time_step 60 -> inside (1)
    # time_step 100 -> after repair (>60, not in horizon) (0)
    df_tte = pd.DataFrame({
        "vehicle_id": ["T1"],
        "repaired": [1],
        "repair_time_step": [60]
    })
    labels_df = generate_horizon_labels(df_readouts, df_tte, horizon=48)
    expected_labels = [0, 0, 1, 1, 1, 0]
    assert labels_df["label"].tolist() == expected_labels


def test_leakage_safeguards_detection():
    """Test that vehicle overlap triggers failure."""
    train_df = pd.DataFrame({"vehicle_id": ["T1", "T2"], "time_step": [0, 0]})
    val_df = pd.DataFrame({"vehicle_id": ["T2", "T3"], "time_step": [0, 0]})
    test_df = pd.DataFrame({"vehicle_id": ["T4"], "time_step": [0]})

    report = validate_leakage_safeguards(train_df, val_df, test_df)
    assert report["vehicle_separation_passed"] is False


from ml.evaluation.metrics import (
    official_scania_cost,
    custom_normalized_cost,
    evaluate_binary_predictions,
    map_time_to_failure_to_proximity_classes
)


def test_official_scania_cost_and_custom_cost():
    """Test official Scania 5-class cost function and custom cost metric."""
    # y_proximity: 0=Healthy, 1=Class 1 (48-24), 4=Class 4 (6-0)
    y_proximity = np.array([0, 0, 1, 4])
    y_binary = np.array([0, 0, 1, 1])
    
    # Predict all 0 (Missed Class 1 and Class 4, No false alarms)
    pred_all_healthy = np.array([0, 0, 0, 0])
    scania_cost_1 = official_scania_cost(y_proximity, pred_all_healthy)
    # Class 1 missed = 200, Class 4 missed = 500 -> Total = 700
    assert scania_cost_1["official_scania_total_cost"] == 700.0

    # Predict all 1 (Timely maintenance on Class 1 and 4, but 2 False Alarms on healthy)
    pred_all_maint = np.array([1, 1, 1, 1])
    scania_cost_2 = official_scania_cost(y_proximity, pred_all_maint)
    # 2 False alarms * 7 = 14. Timely maintenance = 0 -> Total = 14
    assert scania_cost_2["official_scania_total_cost"] == 14.0
    assert scania_cost_2["false_alarm_count"] == 2

    # Custom normalized cost check
    custom_res = custom_normalized_cost(y_binary, pred_all_healthy, c_fn=500, c_fp=10)
    assert custom_res["custom_total_cost"] == 1000.0  # 2 missed failures * 500


def test_end_to_end_single_vehicle_inference():
    """Test end-to-end inference for a single vehicle using saved artifacts."""
    predictor = TruckFailurePredictor()
    
    # Create sample chronological telemetry for 1 truck
    sample_truck = pd.DataFrame({
        "vehicle_id": ["TRUCK_TEST_001"] * 5,
        "time_step": [0, 1, 2, 3, 4],
        "counter_01": [1000.0, 1020.0, 1045.0, 1080.0, 1150.0],
        "counter_02": [500.0, 510.0, 520.0, 530.0, 540.0],
        "counter_03": [200.0, 210.0, 230.0, 260.0, 310.0],
        "counter_04": [800.0, 805.0, 810.0, 815.0, 820.0],
        "counter_05": [300.0, 305.0, 310.0, 315.0, 320.0],
        "counter_06": [400.0, 405.0, 410.0, 415.0, 420.0],
        "counter_07": [150.0, 160.0, 175.0, 200.0, 240.0],
        "counter_08": [600.0, 605.0, 610.0, 615.0, 620.0],
    })
    for i in range(1, 13):
        sample_truck[f"hist_bin_{i:02d}"] = 8.33

    sample_specs = pd.DataFrame({
        "vehicle_id": ["TRUCK_TEST_001"],
        "spec_engine_type": ["ENG_DC13"],
        "spec_chassis_variant": ["CHAS_6x2"],
        "spec_duty_cycle": ["DUTY_LONG_HAUL"],
        "spec_axle_config": ["AXLE_STD"]
    })

    # Predict sequence
    seq_preds = predictor.predict_sequence(sample_truck, sample_specs)
    assert len(seq_preds) == 5
    assert "failure_probability" in seq_preds.columns
    assert "risk_tier" in seq_preds.columns

    # Predict snapshot
    snapshot = predictor.predict_latest_snapshot(sample_truck, sample_specs)
    assert snapshot["vehicle_id"] == "TRUCK_TEST_001"
    assert snapshot["current_time_step"] == 4
    assert 0.0 <= snapshot["failure_probability"] <= 1.0
    assert snapshot["risk_tier"] in ["HEALTHY", "ADVISORY", "WARNING", "CRITICAL"]
    assert "recommendation" in snapshot
