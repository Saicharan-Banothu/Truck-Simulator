# Technical Verification Summary: Industrial Truck Failure Prediction

**Project Title:** PREDICTING INDUSTRIAL TRUCK FAILURES FROM OPERATIONAL TELEMETRY  
**Institution:** Vallurupalli Nageswara Rao Vignana Jyothi Institute of Engineering & Technology (VNR VJIET)  
**Department:** Computer Science and Engineering | B.Tech. Computer Science and Business Systems  
**Course:** Machine Learning Laboratory (Course Code: 22PC2CB302) | Academic Regulation: R25, JNTUH  
**Date:** November 2026  

---

## 1. Project Team & Identity

| Student Name | Roll Number | Academic Role / Technical Contribution |
| :--- | :--- | :--- |
| **B Sathwik** | 24071A3204 | Telemetry Ingestion, Causal Forward-Fill, Dataset Benchmarking, Chapters 1 & 2 |
| **B Sai Charan** | 24071A3206 | Architecture, Signed-Log Transform, Multi-Window Temporal Features, Chapter 3 |
| **K Jayanth Varma** | 24071A3232 | LightGBM Modeling, Hyperparameter Optimization, Cost Sweep, Chapter 4 (Exps 1–5) |
| **Md Sameer** | 24071A3243 | Vehicle Trajectories, Baseline Benchmarks, Pytest Harness, Chapter 4 (Exps 6–7) |
| **P Akshay Kumar** | 24071A3247 | FastAPI REST Server, Browser Digital Twin UI, Chapter 5, QA Compilation |

**Supervisors & Head of Department:**
- **Supervisor 1:** Mr. K. Akhil, Assistant Professor, Department of CSE, VNR VJIET
- **Supervisor 2:** Mrs. G. Lakshmi Deepthi, Assistant Professor, Department of CSE, VNR VJIET
- **Head of Department:** Dr. V Baby, Professor & HOD, Department of CSE, VNR VJIET

---

## 2. Dataset Schema & Empirical Provenance

- **Benchmark Specification:** Standardized SCANIA Component X Schema
- **Data Provenance:** Synthetic benchmark strictly calibrated against published failure rates, noise envelopes, and degradation dynamics of commercial heavy trucks.
- **Total Fleet Size:** 400 mutually exclusive commercial vehicles.
- **Total Observations:** 43,796 time-series records.
- **Splits Partition:**
  - **Training Split:** 250 vehicles | 27,418 observations | 658 positive failures (2.40% positive rate)
  - **Validation Split:** 75 vehicles | 8,295 observations | 189 positive failures (2.28% positive rate)
  - **Held-Out Test Split:** 75 vehicles | 8,083 observations | 192 positive failures (2.38% positive rate)
- **Modalities Recorded:**
  - 8 Continuous Cumulative Operational Counters (`counter_01` to `counter_08`)
  - 12 Bivariate Torque-Speed Operational Histogram Bins (`hist_bin_01` to `hist_bin_12`, summing to 100%)
  - 4 Static Specifications: Engine Family (DC09, DC13, DC16), Chassis Variant (4x2, 6x2, 6x4, 8x4), Haulage Duty Cycle (Long Haul, Distribution, Heavy Haul), Axle Configuration (Standard)
  - Right-censored Time-to-Event (TTE) logs with failure timestamps $T_i^*$.

---

## 3. Mathematical Formulation & Causal Preprocessing

1. **Failure Horizon Definition:**
   $$y_{i,t} = \begin{cases} 1 & \text{if } 0 < (T_i^* - t) \le H = 48 \text{ timesteps} \\ 0 & \text{otherwise} \end{cases}$$
2. **First-Order Causal Differencing:**
   $$\Delta x_t = x_t - x_{t-1} \quad (\Delta x_0 = 0)$$
3. **Non-Linear Signed-Log Outlier Compression:**
   $$g(\Delta x_t) = \text{sign}(\Delta x_t) \cdot \ln(1 + |\Delta x_t|)$$
4. **Train-Only Robust Scaling:**
   $$z_t = \frac{g(\Delta x_t) - Q_{2,\text{train}}}{Q_{3,\text{train}} - Q_{1,\text{train}}}$$
5. **Multi-Window Temporal Feature Vector (210 Features):**
   - 20 Instantaneous Transformed Channels
   - 180 Multi-Window Rolling Features: Mean, Standard Deviation, and Maximum over $W \in \{6, 12, 24\}$ past timesteps
   - 1 Operational Age ($t$)
   - 9 One-Hot Encoded Specification Categories

---

## 4. Machine Learning Model Architecture

- **Classifier:** LightGBM (Light Gradient Boosting Machine)
- **Estimators:** 150 Decision Trees
- **Tree Growth Policy:** Leaf-wise (best-first) tree expansion
- **Maximum Depth:** 6
- **Number of Leaves:** 31
- **Learning Rate ($\eta$):** 0.05
- **Subsampling Rate:** `colsample_bytree = 0.8`, `subsample = 0.8`
- **Class Imbalance Strategy:** Gradient-based class weighting (`scale_pos_weight`)
- **Training Latency:** 3.22 seconds on x86_64 CPU

---

## 5. Verified Empirical Results on Held-Out Test Set (8,083 Samples)

| Evaluation Metric | Measured Value | Baseline ($\theta = 0.50$) | Operational Significance |
| :--- | :--- | :--- | :--- |
| **PR-AUC** | **0.7893** | 0.7893 | Robust discrimination under 2.4% extreme failure imbalance |
| **ROC-AUC** | **0.9303** | 0.9303 | Outstanding ranking separation between failing & healthy trucks |
| **Recall (Sensitivity)** | **77.60%** | 33.33% | Detects 149 of 192 impending breakdown states |
| **Precision** | **50.85%** | 74.42% | Over 50% of workshop dispatch warnings represent verified failures |
| **F1-Score** | **0.6144** | 0.4604 | Balanced operational effectiveness |
| **Optimal Threshold ($\theta^*$)** | **0.0100** | 0.5000 | Tuned against asymmetric maintenance costs |
| **True Positives (TP)** | **149** | 64 | Detected degradation states scheduled for workshop overhaul |
| **False Positives (FP)** | **144** | 22 | Preventive workshop inspection alerts ($10 fee) |
| **True Negatives (TN)** | **7,747** | 7,869 | Healthy fleet vehicles correctly permitted to continue routes |
| **False Negatives (FN)** | **43** | 128 | Slashed missed highway breakdowns from 128 to 43 |
| **Total Maintenance Cost** | **$24,430** | $65,420 | **$40,990 savings (62.7% total cost reduction)** |
| **Cost per Sample** | **$3.02** | $8.09 | Low cost per monitored operating hour |

**Leading Discriminative Features (Split Gain):**
1. `counter_07_delta_log_roll_std_24` (213 splits, 3.95% relative gain) — 24h rolling torque variance in Component X
2. `counter_03_delta_log_roll_std_24` (176 splits, 3.26% relative gain) — Hydraulic pressure stability
3. `counter_01_delta_log_roll_std_24` (175 splits, 3.25% relative gain) — Driveline vibration variance

---

## 6. Software Implementation & Verification

- **Automated Unit Tests:** 6/6 tests passing (100%) in `tests/test_pipeline.py`.
- **Inference Latency:** Sub-millisecond snapshot scoring (< 1.2 ms per vehicle).
- **Backend API:** FastAPI running on `http://localhost:8000` with Swagger docs at `/docs`.
- **Command Center:** Interactive Digital Twin with parameter sliders, real-time risk tiers, and drag-and-drop CSV ingestion.

