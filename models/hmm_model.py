"""
models/hmm_model.py
───────────────────
Gaussian Hidden Markov Model regime detector.
Wraps hmmlearn.hmm.GaussianHMM.
"""

from __future__ import annotations

import numpy as np
from hmmlearn.hmm import GaussianHMM

from .base import BaseRegimeModel


class HMMRegimeModel(BaseRegimeModel):
    """
    Gaussian HMM — models regime as a latent Markov chain.
    Best for capturing *persistence* and smooth state transitions.
    """

    def __init__(self, n_states: int = 5, n_iter: int = 200,
                 random_state: int = 42):
        super().__init__(n_states, random_state)
        self.n_iter = n_iter

    def fit_predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        self._model = GaussianHMM(
            n_components=self.n_states,
            covariance_type="full",
            n_iter=self.n_iter,
            random_state=self.random_state,
            tol=1e-4,
        )
        self._model.fit(X)
        states = self._model.predict(X)
        probs  = self._model.predict_proba(X)
        return states, probs
