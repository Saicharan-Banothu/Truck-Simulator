import os
from pathlib import Path
import numpy as np
import pandas as pd

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def generate_scania_benchmark(
    output_dir: Path = DEFAULT_DATA_DIR,
    n_train_trucks: int = 250,
    n_val_trucks: int = 75,
    n_test_trucks: int = 75,
    failure_rate: float = 0.08,
    random_seed: int = 42
) -> None:
    """
    Generates a realistic synthetic benchmark dataset strictly mirroring the
    SCANIA Component X schema, featuring cumulative operational counters,
    usage histograms, categorical specifications, and right-censored TTE logs.
    """
    np.random.seed(random_seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    splits = [
        ("train", n_train_trucks, 1),
        ("validation", n_val_trucks, n_train_trucks + 1),
        ("test", n_test_trucks, n_train_trucks + n_val_trucks + 1),
    ]

    counter_cols = [f"counter_{i:02d}" for i in range(1, 9)]
    hist_cols = [f"hist_bin_{i:02d}" for i in range(1, 13)]

    engine_types = ["ENG_DC09", "ENG_DC13", "ENG_DC16"]
    chassis_types = ["CHAS_4x2", "CHAS_6x2", "CHAS_6x4", "CHAS_8x4"]
    duty_cycles = ["DUTY_LONG_HAUL", "DUTY_DISTRIBUTION", "DUTY_CONSTRUCTION", "DUTY_HEAVY_HAUL"]
    axle_configs = ["AXLE_STD", "AXLE_REINFORCED"]

    for split_name, n_trucks, start_id in splits:
        specs_rows = []
        readout_rows = []
        tte_rows = []
        labels_rows = []

        for i in range(n_trucks):
            vid = f"TRUCK_{start_id + i:05d}"
            
            # Specs
            spec_eng = np.random.choice(engine_types)
            spec_chas = np.random.choice(chassis_types)
            spec_duty = np.random.choice(duty_cycles)
            spec_axle = np.random.choice(axle_configs)

            specs_rows.append({
                "vehicle_id": vid,
                "spec_engine_type": spec_eng,
                "spec_chassis_variant": spec_chas,
                "spec_duty_cycle": spec_duty,
                "spec_axle_config": spec_axle
            })

            # Sequence length & Failure status
            study_length = int(np.random.randint(60, 160))
            is_failing = np.random.rand() < failure_rate
            
            if is_failing:
                failure_time = int(np.random.randint(45, study_length))
                tte_val = failure_time
                repaired = 1
            else:
                failure_time = None
                tte_val = study_length
                repaired = 0

            tte_rows.append({
                "vehicle_id": vid,
                "length_of_study_time_step": study_length,
                "repaired": repaired,
                "repair_time_step": failure_time if is_failing else -1
            })

            labels_rows.append({
                "vehicle_id": vid,
                "class_label": 1 if is_failing else 0,
                "time_to_event": tte_val
            })

            # Telemetry generation
            # Initial counter values
            base_counters = np.random.uniform(500, 15000, size=8)
            rates = np.random.uniform(10, 80, size=8)
            
            # Severity factor
            severity = 1.0
            if spec_duty == "DUTY_HEAVY_HAUL":
                severity = 1.4
            elif spec_duty == "DUTY_CONSTRUCTION":
                severity = 1.25

            curr_counters = base_counters.copy()
            max_t = failure_time if is_failing else study_length

            for t in range(max_t):
                # Normal operational increment
                step_increment = rates * severity * (1.0 + 0.15 * np.random.randn(8))
                step_increment = np.maximum(step_increment, 0.0)

                # Degradation signature if approaching failure
                if is_failing and (failure_time - t) <= 48:
                    proximity_factor = (48.0 - (failure_time - t)) / 48.0
                    # Component X stress manifests as exponential increase in counters 01, 03, 07
                    step_increment[0] *= (1.0 + 2.8 * proximity_factor)
                    step_increment[2] *= (1.0 + 3.2 * proximity_factor)
                    step_increment[6] *= (1.0 + 2.5 * proximity_factor)

                curr_counters += step_increment

                # Histogram generation (summing to 100%)
                base_hist = np.random.dirichlet(np.ones(12) * 2.0) * 100.0
                if is_failing and (failure_time - t) <= 30:
                    # High stress bins (bins 10, 11, 12) increase
                    shift = (30.0 - (failure_time - t)) / 30.0 * 15.0
                    base_hist[9:] += shift
                    base_hist[:4] = np.maximum(base_hist[:4] - shift / 4.0, 0.0)
                    base_hist = (base_hist / base_hist.sum()) * 100.0

                readout = {
                    "vehicle_id": vid,
                    "time_step": t,
                }
                for c_idx, c_name in enumerate(counter_cols):
                    readout[c_name] = round(float(curr_counters[c_idx]), 2)
                for h_idx, h_name in enumerate(hist_cols):
                    readout[h_name] = round(float(base_hist[h_idx]), 3)

                readout_rows.append(readout)

        # Save files per split
        df_specs = pd.DataFrame(specs_rows)
        df_readouts = pd.DataFrame(readout_rows)
        df_tte = pd.DataFrame(tte_rows)
        df_labels = pd.DataFrame(labels_rows)

        if split_name == "train":
            df_specs.to_csv(output_dir / "train_specifications.csv", index=False)
            df_readouts.to_csv(output_dir / "train_operational_readouts.csv", index=False)
            df_tte.to_csv(output_dir / "train_tte.csv", index=False)
        elif split_name == "validation":
            df_specs.to_csv(output_dir / "validation_specifications.csv", index=False)
            df_readouts.to_csv(output_dir / "validation_operational_readouts.csv", index=False)
            df_labels.to_csv(output_dir / "validation_labels.csv", index=False)
            df_tte.to_csv(output_dir / "validation_tte.csv", index=False)
        elif split_name == "test":
            df_specs.to_csv(output_dir / "test_specifications.csv", index=False)
            df_readouts.to_csv(output_dir / "test_operational_readouts.csv", index=False)
            df_labels.to_csv(output_dir / "test_labels.csv", index=False)
            df_tte.to_csv(output_dir / "test_tte.csv", index=False)

    print(f"Standardized Scania Component X benchmark files generated in '{output_dir}'.")


if __name__ == "__main__":
    generate_scania_benchmark()
