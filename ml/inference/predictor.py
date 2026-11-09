import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ml.features.temporal_features import build_temporal_features


class TruckFailurePredictor:
    """
    Production inference engine for predicting industrial truck failure risks from telemetry.
    Loads frozen preprocessing pipelines, LightGBM models, and optimal decision thresholds.
    """
    def __init__(self, artifacts_dir: Optional[Path] = None):
        if artifacts_dir is None:
            artifacts_dir = PROJECT_ROOT / "ml" / "artifacts"
            
        self.artifacts_dir = Path(artifacts_dir)
        self.model = None
        self.preprocessor = None
        self.feature_config = {}
        self.metadata = {}
        self.optimal_threshold = 0.5
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        model_path = self.artifacts_dir / "lightgbm_model.joblib"
        prep_path = self.artifacts_dir / "preprocessor.joblib"
        feat_path = self.artifacts_dir / "feature_config.json"
        meta_path = self.artifacts_dir / "metadata.json"

        if not model_path.exists() or not prep_path.exists():
            raise FileNotFoundError(
                f"Trained artifacts not found in '{self.artifacts_dir}'. "
                "Please run `ml/training/train_lightgbm.py` first."
            )

        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(prep_path)

        with open(feat_path, "r") as f:
            self.feature_config = json.load(f)

        if meta_path.exists():
            with open(meta_path, "r") as f:
                self.metadata = json.load(f)
                self.optimal_threshold = float(self.metadata.get("optimal_threshold", 0.5))

    def predict_sequence(
        self,
        df_readouts: pd.DataFrame,
        df_specs: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Runs causal feature generation and predictions across an entire chronological telemetry sequence.
        Returns a DataFrame containing probabilities, risk states, and binary thresholded flags.
        """
        df_pre = self.preprocessor.transform(df_readouts, df_specs)
        transformed_num_cols = self.feature_config["transformed_num_cols"]
        feature_names = self.feature_config["feature_names"]
        spec_cols = self.feature_config.get("spec_cols", [])

        X_df, _ = build_temporal_features(df_pre, transformed_num_cols, spec_cols=spec_cols)

        # Ensure all expected columns are present
        for col in feature_names:
            if col not in X_df.columns:
                X_df[col] = 0

        X_mat = X_df[feature_names].values
        probas = self.model.predict_proba(X_mat)[:, 1]
        preds = (probas >= self.optimal_threshold).astype(int)

        res = df_readouts[["vehicle_id", "time_step"]].copy().reset_index(drop=True)
        res["failure_probability"] = np.round(probas, 4)
        res["predicted_failure_risk"] = preds
        res["optimal_threshold"] = self.optimal_threshold
        
        # Risk tier definition
        risk_tiers = []
        for p in probas:
            if p >= self.optimal_threshold * 1.5 or p >= 0.7:
                risk_tiers.append("CRITICAL")
            elif p >= self.optimal_threshold:
                risk_tiers.append("WARNING")
            elif p >= self.optimal_threshold * 0.5:
                risk_tiers.append("ADVISORY")
            else:
                risk_tiers.append("HEALTHY")
        res["risk_tier"] = risk_tiers
        return res

    def predict_latest_snapshot(
        self,
        df_history_readouts: pd.DataFrame,
        df_specs: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Computes the failure prediction and risk score for the most recent observation in the history.
        """
        seq_res = self.predict_sequence(df_history_readouts, df_specs)
        latest_row = seq_res.iloc[-1]
        
        vid = str(latest_row["vehicle_id"])
        t = int(latest_row["time_step"])
        prob = float(latest_row["failure_probability"])
        is_risk = bool(latest_row["predicted_failure_risk"] == 1)
        tier = str(latest_row["risk_tier"])

        # Operational recommendation based on risk tier
        if tier == "CRITICAL":
            recommendation = "IMMEDIATE ACTION REQUIRED: High probability of Component X failure within 48h horizon. Ground vehicle for workshop inspection."
        elif tier == "WARNING":
            recommendation = "WARNING: Elevating failure risk detected. Schedule workshop maintenance at next scheduled depot stop."
        elif tier == "ADVISORY":
            recommendation = "ADVISORY: Minor telemetry drift detected. Monitor operational counters closely."
        else:
            recommendation = "NORMAL: Component telemetry operating within healthy baseline parameters."

        return {
            "vehicle_id": vid,
            "current_time_step": t,
            "failure_probability": prob,
            "risk_flag": is_risk,
            "risk_tier": tier,
            "optimal_decision_threshold": self.optimal_threshold,
            "prediction_horizon_timesteps": self.feature_config.get("prediction_horizon", 48),
            "recommendation": recommendation,
        }
