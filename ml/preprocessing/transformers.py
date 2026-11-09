import numpy as np
import pandas as pd
from typing import List, Optional, Tuple, Dict
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import RobustScaler


class CausalDeltaLogTransformer(BaseEstimator, TransformerMixin):
    """
    Computes causal first-order differences per vehicle and applies signed-log transformation:
        delta_t = x_t - x_(t-1)  (delta_0 = 0)
        transformed = sign(delta) * log1p(abs(delta))
    """
    def __init__(self, numeric_cols: Optional[List[str]] = None):
        self.numeric_cols = numeric_cols or []

    def fit(self, X: pd.DataFrame, y=None):
        if not self.numeric_cols:
            self.numeric_cols = [
                c for c in X.columns 
                if c not in ["vehicle_id", "time_step"] and np.issubdtype(X[c].dtype, np.number)
            ]
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        df = X.copy()
        df = df.sort_values(["vehicle_id", "time_step"])
        
        deltas = df.groupby("vehicle_id")[self.numeric_cols].diff().fillna(0.0)
        signed_log_deltas = np.sign(deltas) * np.log1p(np.abs(deltas))
        signed_log_deltas.columns = [f"{col}_delta_log" for col in self.numeric_cols]
        
        res = pd.concat([df[["vehicle_id", "time_step"]].reset_index(drop=True), signed_log_deltas.reset_index(drop=True)], axis=1)
        return res


class CausalSequencePreprocessor:
    """
    Schema-driven causal preprocessing pipeline:
    - Invariant to custom column names (handles anonymized real SCANIA columns as well as synthetic).
    - Detects numeric and categorical features automatically if not explicitly provided.
    - Fits imputation medians and RobustScaler strictly on training data.
    - Applies frozen transforms to validation, test, and inference streams.
    """
    def __init__(
        self,
        numeric_cols: Optional[List[str]] = None,
        spec_cols: Optional[List[str]] = None,
        counter_cols: Optional[List[str]] = None,
        hist_cols: Optional[List[str]] = None
    ):
        self.numeric_cols = numeric_cols or []
        if not self.numeric_cols and (counter_cols or hist_cols):
            self.numeric_cols = (counter_cols or []) + (hist_cols or [])
            
        self.spec_cols = spec_cols or []
        self.train_impute_medians: Dict[str, float] = {}
        self.scaler = RobustScaler()
        self.is_fitted = False
        self.transformed_feature_names: List[str] = []

    def _discover_schema(self, df_readouts: pd.DataFrame, df_specs: Optional[pd.DataFrame] = None) -> None:
        """Dynamically infer numeric and categorical column sets if not provided."""
        if not self.numeric_cols:
            self.numeric_cols = [
                c for c in df_readouts.columns 
                if c not in ["vehicle_id", "time_step"] and np.issubdtype(df_readouts[c].dtype, np.number)
            ]
        if df_specs is not None and not self.spec_cols:
            self.spec_cols = [c for c in df_specs.columns if c != "vehicle_id"]

    def fit(self, df_readouts: pd.DataFrame, df_specs: Optional[pd.DataFrame] = None) -> "CausalSequencePreprocessor":
        """Fit imputation medians and scalers strictly on training data."""
        self._discover_schema(df_readouts, df_specs)
        df = df_readouts.copy()
        
        # 1. Training medians for imputation
        for col in self.numeric_cols:
            self.train_impute_medians[col] = float(df[col].median() if col in df else 0.0)

        # 2. Impute & Causal differencing
        df_imputed = self._impute(df)
        df_deltas = self._compute_deltas(df_imputed)
        
        delta_cols = [c for c in df_deltas.columns if c not in ["vehicle_id", "time_step"]]
        
        # 3. Fit RobustScaler
        self.scaler.fit(df_deltas[delta_cols])
        self.transformed_feature_names = delta_cols
        self.is_fitted = True
        return self

    def _impute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Causally forward fill per vehicle, then fill remaining leading NaNs with train medians."""
        sorted_df = df.sort_values(["vehicle_id", "time_step"]).copy()
        sorted_df[self.numeric_cols] = sorted_df.groupby("vehicle_id")[self.numeric_cols].ffill()
        for col in self.numeric_cols:
            sorted_df[col] = sorted_df[col].fillna(self.train_impute_medians.get(col, 0.0))
        return sorted_df

    def _compute_deltas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute delta_t = x_t - x_(t-1) and apply sign(delta) * log1p(|delta|)."""
        deltas = df.groupby("vehicle_id")[self.numeric_cols].diff().fillna(0.0)
        signed_log = np.sign(deltas) * np.log1p(np.abs(deltas))
        signed_log.columns = [f"{col}_delta_log" for col in self.numeric_cols]
        
        out = pd.concat([df[["vehicle_id", "time_step"]].reset_index(drop=True), signed_log.reset_index(drop=True)], axis=1)
        return out

    def transform(self, df_readouts: pd.DataFrame, df_specs: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Transform readouts using frozen training parameters."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted on training data before calling transform.")
        
        df = df_readouts.copy()
        df_imputed = self._impute(df)
        df_deltas = self._compute_deltas(df_imputed)
        
        scaled_values = self.scaler.transform(df_deltas[self.transformed_feature_names])
        scaled_df = pd.DataFrame(scaled_values, columns=self.transformed_feature_names)
        
        res = pd.concat([df_deltas[["vehicle_id", "time_step"]].reset_index(drop=True), scaled_df.reset_index(drop=True)], axis=1)
        
        if df_specs is not None and len(self.spec_cols) > 0:
            existing_specs = [c for c in self.spec_cols if c in df_specs.columns]
            if existing_specs:
                res = res.merge(df_specs[["vehicle_id"] + existing_specs], on="vehicle_id", how="left")
            
        return res
