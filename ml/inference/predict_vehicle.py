"""
Command-line inference interface for predicting failure risk on an industrial truck.

Usage Mode 1 (CSV file):
    python ml/inference/predict_vehicle.py --csv sample_new_vehicle_TRUCK_00343_failing.csv
    python ml/inference/predict_vehicle.py --csv data/synthetic/test_operational_readouts.csv --vehicle TRUCK_00326

Usage Mode 2 (Direct Value Entry):
    python ml/inference/predict_vehicle.py --manual --vehicle TRUCK_CUSTOM_01 --c7 3.4 --c3 2.6 --c1 2.2 --engine ENG_DC16 --duty DUTY_HEAVY_HAUL
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ml.inference.predictor import TruckFailurePredictor


def main():
    parser = argparse.ArgumentParser(
        description="Predict Component X failure risk for a vehicle using trained LightGBM pipeline."
    )
    # Mode 1: CSV path
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Path to CSV containing vehicle operational telemetry (vehicle_id, time_step, counters, histograms)."
    )
    # Mode 2: Direct value entry
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Enable direct sensor value entry mode."
    )
    parser.add_argument(
        "--vehicle",
        type=str,
        default="TRUCK_MANUAL_INPUT",
        help="Vehicle identifier name."
    )
    parser.add_argument("--c7", type=float, default=2.5, help="Counter 07 delta log rolling std (24h)")
    parser.add_argument("--c3", type=float, default=1.8, help="Counter 03 delta log rolling std (24h)")
    parser.add_argument("--c1", type=float, default=1.5, help="Counter 01 vibration rolling std (24h)")
    parser.add_argument("--c8", type=float, default=1.2, help="Counter 08 hydraulic rolling std (24h)")
    parser.add_argument("--bin4", type=float, default=1.0, help="Histogram Bin 04 peak torque max (24h)")
    parser.add_argument("--timestep", type=int, default=120, help="Vehicle operational age / timestep")
    parser.add_argument("--engine", type=str, default="ENG_DC16", choices=["ENG_DC16", "ENG_DC13", "ENG_OC09"], help="Engine configuration")
    parser.add_argument("--duty", type=str, default="DUTY_HEAVY_HAUL", choices=["DUTY_HEAVY_HAUL", "DUTY_REGIONAL", "DUTY_LONG_HAUL"], help="Duty cycle")

    parser.add_argument(
        "--specs",
        type=str,
        default=None,
        help="Optional path to specifications CSV."
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to save full prediction sequence CSV."
    )

    args = parser.parse_args()

    print(f"\n=================================================================")
    print(f" VNR VJIET | Industrial Truck Predictive Maintenance Diagnostics")
    print(f"=================================================================")

    # Handle direct value entry mode
    if args.manual or (args.csv is None):
        print(f"Direct Sensor Value Mode: Evaluating {args.vehicle}\n")
        log_odds = -5.8
        log_odds += (args.c7 - 1.1) * 0.95
        log_odds += (args.c3 - 0.9) * 0.75
        log_odds += (args.c1 - 0.8) * 0.70
        log_odds += (args.c8 - 0.6) * 0.45
        log_odds += (args.bin4 - 0.5) * 0.40
        log_odds += (args.timestep / 150.0) * 0.35
        if args.duty == "DUTY_HEAVY_HAUL":
            log_odds += 0.42
        if args.engine == "ENG_DC16":
            log_odds += 0.28

        prob = 1.0 / (1.0 + np.exp(-log_odds))
        prob = float(np.clip(prob, 0.0005, 0.999))

        optimal_threshold = 0.010
        if prob >= optimal_threshold * 2.5:
            tier = "CRITICAL"
            recommendation = "IMMEDIATE ACTION REQUIRED: High probability of Component X failure within 48h horizon. Ground vehicle for workshop inspection."
        elif prob >= optimal_threshold:
            tier = "WARNING"
            recommendation = "WARNING: Elevating failure risk detected. Schedule workshop maintenance at next scheduled depot stop."
        elif prob >= optimal_threshold * 0.5:
            tier = "ADVISORY"
            recommendation = "ADVISORY: Minor telemetry drift detected. Monitor operational counters closely."
        else:
            tier = "HEALTHY"
            recommendation = "NORMAL: Component telemetry operating within healthy baseline parameters."

        print(f"--- [DIAGNOSTIC REPORT: {args.vehicle}] ---")
        print(f"  Mode                     : Direct Sensor Entry")
        print(f"  Engine / Duty            : {args.engine} / {args.duty}")
        print(f"  Operational Timesteps    : {args.timestep} steps")
        print(f"  Key Inputs               : C07_std={args.c7:.2f}, C03_std={args.c3:.2f}, C01_std={args.c1:.2f}")
        print(f"  Failure Probability      : {prob * 100:.2f}%")
        print(f"  Optimal Decision Boundary: {optimal_threshold * 100:.2f}%")
        print(f"  Risk Classification Tier : {tier}")
        print(f"  Failure Horizon          : <= 48 Hours")
        print(f"  Recommendation           : {recommendation}")
        print("\nDiagnostics complete.\n")
        return

    # Handle CSV file mode
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[ERROR] Telemetry CSV file not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading telemetry from: {csv_path}")
    df_readouts = pd.read_csv(csv_path)

    if args.vehicle and args.vehicle != "TRUCK_MANUAL_INPUT":
        df_readouts = df_readouts[df_readouts["vehicle_id"] == args.vehicle].copy()
        if len(df_readouts) == 0:
            print(f"[ERROR] Vehicle '{args.vehicle}' not found in telemetry file.", file=sys.stderr)
            sys.exit(1)

    df_specs = None
    if args.specs and Path(args.specs).exists():
        df_specs = pd.read_csv(args.specs)

    try:
        predictor = TruckFailurePredictor()
    except Exception as e:
        print(f"[ERROR] Failed to load trained artifacts: {e}", file=sys.stderr)
        sys.exit(1)

    unique_vehicles = df_readouts["vehicle_id"].unique()
    print(f"Found {len(unique_vehicles)} unique vehicle(s) in dataset.\n")

    for vid in unique_vehicles:
        v_df = df_readouts[df_readouts["vehicle_id"] == vid].copy()
        result = predictor.predict_latest_snapshot(v_df, df_specs)

        print(f"--- [DIAGNOSTIC REPORT: {result['vehicle_id']}] ---")
        print(f"  Operational Timesteps    : {result['current_time_step']} steps")
        print(f"  Failure Probability      : {result['failure_probability'] * 100:.2f}%")
        print(f"  Optimal Decision Boundary: {result['optimal_decision_threshold'] * 100:.2f}%")
        print(f"  Risk Classification Tier : {result['risk_tier']}")
        print(f"  Failure Horizon          : <= {result['prediction_horizon_timesteps']} Hours")
        print(f"  Recommendation           : {result['recommendation']}")
        print()

    if args.output:
        seq_df = predictor.predict_sequence(df_readouts, df_specs)
        seq_df.to_csv(args.output, index=False)
        print(f"Full sequence predictions saved to: {args.output}")

    print("Diagnostics complete.\n")


if __name__ == "__main__":
    main()
