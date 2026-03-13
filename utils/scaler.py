"""
utils/scaler.py
───────────────
Thin wrapper around StandardScaler so models don't import sklearn directly.
"""

from __future__ import annotations

import numpy as np
from sklearn.preprocessing import StandardScaler


def scale_features(X: np.ndarray) -> tuple[np.ndarray, StandardScaler]:
    """Fit-transform X, return (scaled_X, fitted_scaler)."""
    sc = StandardScaler()
    return sc.fit_transform(X), sc
