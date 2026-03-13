"""
models/gmm_model.py
───────────────────
Gaussian Mixture Model regime detector.
Wraps sklearn.mixture.GaussianMixture.
"""

from __future__ import annotations

import numpy as np
from sklearn.mixture import GaussianMixture

from .base import BaseRegimeModel


class GMMRegimeModel(BaseRegimeModel):
    """
    GMM — fits a mixture of Gaussians to the feature space.
    No temporal dependency; each bar is classified independently.
    """

    def __init__(self, n_states: int = 5, n_init: int = 5,
                 random_state: int = 42):
        super().__init__(n_states, random_state)
        self.n_init = n_init

    def fit_predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        self._model = GaussianMixture(
            n_components=self.n_states,
            covariance_type="full",
            n_init=self.n_init,
            random_state=self.random_state,
        )
        self._model.fit(X)
        states = self._model.predict(X)
        probs  = self._model.predict_proba(X)
        return states, probs
