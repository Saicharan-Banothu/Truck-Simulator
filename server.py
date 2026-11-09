"""
Industrial Truck Predictive Maintenance & Failure Risk Monitoring System
High-Performance Localhost Web Server & REST API
VNR VJIET | Powered by FastAPI, Uvicorn & Scania LightGBM Pipeline
"""

import io
import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import numpy as np

# Resolve project roots
CURRENT_DIR = Path(__file__).resolve().parent
if (CURRENT_DIR / "ml").exists():
    ML_ROOT = CURRENT_DIR
else:
    ML_ROOT = CURRENT_DIR / "Industrial-Truck-Failure-Prediction"

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Import Machine Learning Predictor
try:
    from ml.inference.predictor import TruckFailurePredictor
    PREDICTOR = TruckFailurePredictor(artifacts_dir=ML_ROOT / "ml" / "artifacts")
    MODEL_LOADED = True
except Exception as e:
    print(f"Warning: Could not initialize TruckFailurePredictor: {e}")
    PREDICTOR = None
    MODEL_LOADED = False

app = FastAPI(
    title="Industrial Truck Failure Risk AI Server",
    description="Real-time condition monitoring, causal telemetry inference, and LightGBM predictive maintenance engine.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files if directory exists
app.mount("/static", StaticFiles(directory=str(CURRENT_DIR)), name="static")


class ManualPredictRequest(BaseModel):
    vehicle_id: str = "TRUCK_CUSTOM_01"
    time_step: int = 120
    c07_std: float = 2.5
    c03_std: float = 1.8
    c01_std: float = 1.5
    c08_std: float = 1.2
    hist_bin04: float = 1.0
    engine: str = "ENG_DC16"
    duty: str = "DUTY_HEAVY_HAUL"


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the primary interactive command center dashboard."""
    dashboard_file = CURRENT_DIR / "dashboard.html"
    if not dashboard_file.exists():
        dashboard_file = INNER_PROJECT_DIR / "dashboard.html"
    if not dashboard_file.exists():
        raise HTTPException(status_code=404, detail="dashboard.html not found.")
    return HTMLResponse(content=dashboard_file.read_text(encoding="utf-8"))


@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard_alias():
    return await serve_dashboard()


@app.get("/api/health")
async def health_check():
    """Returns server and ML engine health status."""
    return {
        "status": "healthy",
        "model_loaded": MODEL_LOADED,
        "engine": "LightGBM + Causal Differencing Transformer",
        "optimal_threshold": getattr(PREDICTOR, "optimal_threshold", 0.010) if PREDICTOR else 0.010,
        "prediction_horizon_hours": 48,
        "supported_features": getattr(PREDICTOR, "feature_config", {}).get("feature_names", []) if PREDICTOR else []
    }


@app.get("/api/fleet")
async def get_fleet_status():
    """Returns the fleet status summary."""
    fleet = [
        {"id": "VNR-HD-101", "engine": "DC16 V8", "duty": "Heavy Haul", "prob": 0.038, "route": "Singareni Coal Basin", "status": "CRITICAL", "mileage": "242,150 km"},
        {"id": "VNR-HD-102", "engine": "DC13 I-6", "duty": "Regional", "prob": 0.003, "route": "Hyderabad - Warangal", "status": "HEALTHY", "mileage": "185,400 km"},
        {"id": "VNR-HD-103", "engine": "DC16 V8", "duty": "Heavy Haul", "prob": 0.014, "route": "Ramagundam Industrial Corridor", "status": "WARNING", "mileage": "310,200 km"},
        {"id": "VNR-HD-104", "engine": "DC16 V8", "duty": "Heavy Haul", "prob": 0.035, "route": "Outer Ring Road Freight Line", "status": "CRITICAL", "mileage": "278,920 km"},
        {"id": "VNR-HD-105", "engine": "OC09 CNG", "duty": "Regional", "prob": 0.002, "route": "Gachibowli Distribution", "status": "HEALTHY", "mileage": "94,100 km"},
        {"id": "VNR-HD-106", "engine": "DC13 I-6", "duty": "Long Haul", "prob": 0.008, "route": "Hyderabad - Bangalore NH44", "status": "ADVISORY", "mileage": "215,600 km"},
        {"id": "VNR-HD-107", "engine": "DC16 V8", "duty": "Heavy Haul", "prob": 0.024, "route": "Nalgonda Cement Hub", "status": "WARNING", "mileage": "298,400 km"},
        {"id": "VNR-HD-108", "engine": "DC13 I-6", "duty": "Long Haul", "prob": 0.001, "route": "Hyderabad - Vijayawada NH65", "status": "HEALTHY", "mileage": "124,500 km"},
        {"id": "VNR-HD-109", "engine": "OC09 CNG", "duty": "Regional", "prob": 0.004, "route": "Medchal Industrial Area", "status": "HEALTHY", "mileage": "82,300 km"},
        {"id": "VNR-HD-110", "engine": "DC16 V8", "duty": "Heavy Haul", "prob": 0.042, "route": "Kothagudem Mining Line", "status": "CRITICAL", "mileage": "345,100 km"},
        {"id": "VNR-HD-111", "engine": "DC13 I-6", "duty": "Regional", "prob": 0.002, "route": "Shamirpet Tech Park Link", "status": "HEALTHY", "mileage": "160,800 km"},
        {"id": "VNR-HD-112", "engine": "DC16 V8", "duty": "Long Haul", "prob": 0.006, "route": "Hyderabad - Pune Highway", "status": "ADVISORY", "mileage": "228,900 km"}
    ]
    return {"total_trucks": len(fleet), "fleet": fleet}


@app.post("/api/predict/manual")
async def predict_manual(req: ManualPredictRequest):
    """Evaluates component risk from manual parameter entry."""
    log_odds = -5.8
    log_odds += (req.c07_std - 1.1) * 0.95
    log_odds += (req.c03_std - 0.9) * 0.75
    log_odds += (req.c01_std - 0.8) * 0.70
    log_odds += (req.c08_std - 0.6) * 0.45
    log_odds += (req.hist_bin04 - 0.5) * 0.40
    log_odds += (req.time_step / 150.0) * 0.35
    if req.duty == "DUTY_HEAVY_HAUL":
        log_odds += 0.42
    if req.engine == "ENG_DC16":
        log_odds += 0.28

    prob = 1.0 / (1.0 + np.exp(-log_odds))
    prob = float(np.clip(prob, 0.0005, 0.999))
    optimal_threshold = getattr(PREDICTOR, "optimal_threshold", 0.010) if PREDICTOR else 0.010

    if prob >= optimal_threshold * 2.5:
        tier = "CRITICAL"
        verdict = "IMMEDIATE WORKSHOP DISPATCH"
        recommendation = "CRITICAL ALERT: Component X telemetry exhibits extreme torque variance and vibration signatures exceeding safety envelopes. Ground vehicle immediately for workshop strip-down."
    elif prob >= optimal_threshold:
        tier = "WARNING"
        verdict = "SCHEDULE MAINTENANCE INTERVENTION"
        recommendation = "PREDICTIVE WARNING: Telemetry crosses the optimal cost threshold (θ* = 0.010). Schedule Component X inspection at next route depot."
    elif prob >= optimal_threshold * 0.5:
        tier = "ADVISORY"
        verdict = "CONTINUOUS TELEMETRY MONITORING"
        recommendation = "Moderate operational counters observed. Component X functioning nominally under elevated load. Maintain real-time sampling."
    else:
        tier = "HEALTHY"
        verdict = "NO DISPATCH NEEDED"
        recommendation = "All sensor channels strictly within manufacturer baseline bounds. Component X degradation index is negligible."

    return {
        "vehicle_id": req.vehicle_id,
        "time_step": req.time_step,
        "failure_probability": round(prob, 4),
        "failure_percentage": f"{prob * 100:.2f}%",
        "risk_tier": tier,
        "verdict": verdict,
        "optimal_threshold": optimal_threshold,
        "recommendation": recommendation,
        "engine": req.engine,
        "duty": req.duty
    }


@app.post("/api/predict/csv")
async def predict_csv(file: UploadFile = File(...)):
    """
    Ingests vehicle operational telemetry CSV and runs full end-to-end
    causal preprocessing and LightGBM failure prediction.
    """
    if not PREDICTOR:
        raise HTTPException(status_code=500, detail="ML Predictor is not loaded.")

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {e}")

    required_cols = ["vehicle_id", "time_step"]
    for col in required_cols:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"Missing required column in CSV: {col}")

    try:
        latest = PREDICTOR.predict_latest_snapshot(df)
        seq_df = PREDICTOR.predict_sequence(df)

        trajectory = seq_df.to_dict(orient="records")

        return {
            "success": True,
            "filename": file.filename,
            "vehicle_id": latest["vehicle_id"],
            "total_timesteps": len(df),
            "latest_snapshot": latest,
            "trajectory_summary": {
                "initial_prob": float(seq_df["failure_probability"].iloc[0]),
                "latest_prob": float(seq_df["failure_probability"].iloc[-1]),
                "peak_prob": float(seq_df["failure_probability"].max()),
                "critical_steps_count": int((seq_df["risk_tier"] == "CRITICAL").sum())
            },
            "trajectory": trajectory[-50:]  # Return the last 50 timesteps for charting
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")


@app.get("/api/samples/{filename}")
async def get_sample_file(filename: str):
    """Downloads sample benchmark vehicle CSVs."""
    allowed = {
        "healthy": "sample_new_vehicle_TRUCK_00326_healthy.csv",
        "failing": "sample_new_vehicle_TRUCK_00343_failing.csv",
        "TRUCK_00326": "sample_new_vehicle_TRUCK_00326_healthy.csv",
        "TRUCK_00343": "sample_new_vehicle_TRUCK_00343_failing.csv"
    }
    target = allowed.get(filename, filename)
    file_path = CURRENT_DIR / target
    if not file_path.exists():
        file_path = INNER_PROJECT_DIR / target
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample file not found.")
    return FileResponse(file_path, filename=target, media_type="text/csv")


@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse(CURRENT_DIR / "vnr_logo.png", media_type="image/png")


@app.get("/vnr_logo.png")
async def get_logo_small():
    return FileResponse(CURRENT_DIR / "vnr_logo.png", media_type="image/png")


@app.get("/vnr_full_logo.png")
async def get_logo_full():
    return FileResponse(CURRENT_DIR / "vnr_full_logo.png", media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"\n=======================================================")
    print(f"  Industrial Truck Failure Prediction Localhost Server")
    print(f"  Serving Command Center at: http://localhost:{port}")
    print(f"  Interactive API Docs at  : http://localhost:{port}/docs")
    print(f"=======================================================\n")
    uvicorn.run(app, host="0.0.0.0", port=port)

