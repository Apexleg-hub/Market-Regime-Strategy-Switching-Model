"""models/hmm_detector.py - Gaussian HMM detector"""
from __future__ import annotations
import numpy as np
from typing import Tuple
from .base import BaseRegimeDetector

class HMMDetector(BaseRegimeDetector):
    def __init__(self, n_states=5, n_iter=200, random_state=42):
        super().__init__(n_states=n_states, random_state=random_state)
        self.n_iter = n_iter

    def _fit_predict(self, Xs: np.ndarray) -> Tuple[np.ndarray, np.ndarray, object]:
        from hmmlearn.hmm import GaussianHMM
        model = GaussianHMM(n_components=self.n_states, covariance_type="full",
                            n_iter=self.n_iter, random_state=self.random_state, tol=1e-4)
        model.fit(Xs)
        return model.predict(Xs), model.predict_proba(Xs), model
