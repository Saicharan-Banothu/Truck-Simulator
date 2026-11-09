import lightgbm as lgb
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List


def create_lightgbm_model(
    n_estimators: int = 200,
    learning_rate: float = 0.05,
    max_depth: int = 5,
    num_leaves: int = 31,
    scale_pos_weight: float = 5.0,
    random_state: int = 42
) -> lgb.LGBMClassifier:
    """
    Creates a tuned LightGBM classifier with class weighting
    for imbalanced industrial failure telemetry.
    """
    model = lgb.LGBMClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        num_leaves=num_leaves,
        scale_pos_weight=scale_pos_weight,
        random_state=random_state,
        n_jobs=-1,
        verbose=-1
    )
    return model


def get_feature_importances(
    model: lgb.LGBMClassifier,
    feature_names: List[str]
) -> pd.DataFrame:
    """Extracts normalized feature importance dataframe."""
    importances = model.feature_importances_
    df_imp = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values("importance", ascending=False).reset_index(drop=True)
    
    total = df_imp["importance"].sum()
    df_imp["relative_importance"] = df_imp["importance"] / (total if total > 0 else 1.0)
    return df_imp
