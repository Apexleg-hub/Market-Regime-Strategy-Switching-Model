"""
models/regime_mapper.py
───────────────────────
Maps raw integer cluster labels (0..k-1) produced by any detector
onto the five canonical semantic regimes defined in config.constants.

The mapping is purely rule-based on per-cluster feature statistics,
so it works identically for HMM, GMM, and K-Means output.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config.constants import FEATURE_COLS


def map_to_semantic_regimes(raw_states: np.ndarray, df: pd.DataFrame) -> np.ndarray:
    """
    Translate raw cluster IDs → semantic regime IDs (0-4).

    Regime IDs
    ----------
    0  Bull Trend
    1  Bear Trend
    2  High Volatility
    3  Low Volatility
    4  Range Market

    Parameters
    ----------
    raw_states : (n_samples,) integer cluster labels from the detector
    df         : feature-engineered DataFrame aligned with raw_states

    Returns
    -------
    np.ndarray (n_samples,) with values in {0,1,2,3,4}
    """
    regime_map: dict[int, int] = {}

    q75_vol  = df["vol_20"].quantile(0.75)
    q25_bb   = df["bb_width"].quantile(0.25)
    q65_tr   = df["trend_strength"].quantile(0.65)
    q35_tr   = df["trend_strength"].quantile(0.35)

    for s in np.unique(raw_states):
        mask = raw_states == s
        sub  = df[mask]

        avg_trend = sub["trend_strength"].mean()
        avg_vol   = sub["vol_20"].mean()
        avg_slope = sub["ma_slope"].mean()
        avg_bb    = sub["bb_width"].mean()

        if avg_vol > q75_vol:
            regime_map[s] = 2          # High Volatility
        elif avg_bb < q25_bb:
            regime_map[s] = 3          # Low Volatility
        elif avg_trend > q65_tr and avg_slope > 0:
            regime_map[s] = 0          # Bull Trend
        elif avg_trend < q35_tr and avg_slope < 0:
            regime_map[s] = 1          # Bear Trend
        else:
            regime_map[s] = 4          # Ranging

    return np.array([regime_map[s] for s in raw_states])
