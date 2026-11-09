# Industrial Truck Predictive Maintenance & Failure Risk Monitoring System

A condition-based predictive maintenance system for heavy-duty industrial trucks based on the **SCANIA Component X** benchmark.

---

## 🏗️ Architecture & Pipeline Overview

```
 ┌──────────────────────────────────────────────────────────┐
 │               RAW TELEMETRY INGESTION                    │
 │  - Operational Counters (Lifetime distance, hours, etc.) │
 │  - Operational Histograms (Speed vs Torque bins)         │
 │  - Vehicle Specifications (Engine, Chassis, Duty Cycle)  │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │            CAUSAL PREPROCESSING PIPELINE                 │
 │  1. Chronological sorting per vehicle                    │
 │  2. Causal forward-fill & training-only median impute    │
 │  3. First-order differencing: Δt = x_t - x_(t-1)         │
 │  4. Signed-log transform: sign(Δ) * ln(1 + |Δ|)          │
 │  5. RobustScaler (Fitted STRICTLY on training split)     │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │              TEMPORAL FEATURE EXTRACTION                 │
 │  - Instantaneous delta-log readouts                      │
 │  - Causal rolling mean, std, max over windows (6, 12, 24)│
 │  - Operational age (time_step)                           │
 │  - Categorical specification one-hot encodings           │
 └────────────────────────────┬─────────────────────────────┘
                              │
                              ▼
 ┌──────────────────────────────────────────────────────────┐
 │              PREDICTIVE MODELING & INFERENCE             │
 │  - Model: Tuned LightGBM Classifier                      │
 │  - Target: Causal Failure Horizon (Horizon = 48 steps)   │
 │  - Threshold Optimization: Scania Industrial Cost Matrix │
 └──────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```text
Industrial-Truck-Failure-Prediction/
├── ml/
│   ├── data/
│   │   ├── dataset_loader.py               # Dataset discovery & integrity checks
│   │   ├── inspect_dataset.py              # Milestone 1A inspection script
│   │   └── generate_synthetic_benchmark.py # Standardized benchmark generator
│   ├── preprocessing/
│   │   └── transformers.py                 # Causal differencing, signed-log & RobustScaler
│   ├── features/
│   │   └── temporal_features.py            # Label generation, temporal summaries, leakage checks
│   ├── models/
│   │   └── lightgbm_baseline.py            # LightGBM classifier & feature importance
│   ├── training/
│   │   └── train_lightgbm.py               # Leak-free training & threshold tuning pipeline
│   ├── evaluation/
│   │   └── metrics.py                      # PR-AUC, ROC-AUC, F1 & Scania Cost Matrix
│   ├── inference/
│   │   └── predictor.py                    # Standalone inference & snapshot diagnostics
│   └── artifacts/
│       ├── lightgbm_model.joblib           # Trained LightGBM model
│       ├── preprocessor.joblib             # Fitted causal preprocessor
│       ├── feature_config.json             # Feature schema configuration
│       └── metadata.json                   # Optimal threshold, validation & test metrics
├── data/
│   └── raw/                                # Raw Scania CSV files
├── tests/
│   └── test_pipeline.py                    # Pytest test suite (100% pass)
└── docs/
```

---

## 🚀 Getting Started

### 0. Launch Web Command Center & Simulator
```bash
python server.py
# Or on Windows, run start_server.bat
```
- **Dashboard UI**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 1. Inspect Dataset
```bash
python ml/data/inspect_dataset.py
```

### 2. Run Leak-Free Training & Evaluation Pipeline
```bash
python ml/training/train_lightgbm.py
```

### 3. Run Inference on a Sample Vehicle
```bash
python ml/inference/predict_vehicle.py --csv sample_new_vehicle_TRUCK_00343_failing.csv
```

### 4. Run Unit Tests
```bash
python -m pytest tests/ -v
```
