"""models/gmm_detector.py - Gaussian Mixture Model detector"""
from __future__ import annotations
import numpy as np
from typing import Tuple
from .base import BaseRegimeDetector

class GMMDetector(BaseRegimeDetector):
    def __init__(self, n_states=5, n_init=5, random_state=42):
        super().__init__(n_states=n_states, random_state=random_state)
        self.n_init = n_init

    def _fit_predict(self, Xs: np.ndarray) -> Tuple[np.ndarray, np.ndarray, object]:
        from sklearn.mixture import GaussianMixture
        model = GaussianMixture(n_components=self.n_states, covariance_type="full",
                                n_init=self.n_init, random_state=self.random_state)
        model.fit(Xs)
        return model.predict(Xs), model.predict_proba(Xs), model
