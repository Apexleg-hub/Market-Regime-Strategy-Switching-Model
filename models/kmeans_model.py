"""
models/kmeans_model.py
──────────────────────
K-Means clustering regime detector.
Wraps sklearn.cluster.KMeans with soft-assignment via inverse distance.
"""

from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans

from .base import BaseRegimeModel


class KMeansRegimeModel(BaseRegimeModel):
    """
    K-Means clustering — partitions feature space into k hard clusters.
    Soft probabilities derived from normalised inverse euclidean distance.
    """

    def __init__(self, n_states: int = 5, n_init: int = 20,
                 random_state: int = 42):
        super().__init__(n_states, random_state)
        self.n_init = n_init

    def fit_predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        self._model = KMeans(
            n_clusters=self.n_states,
            n_init=self.n_init,
            random_state=self.random_state,
        )
        states = self._model.fit_predict(X)

        # Soft assignment via exponential inverse distance
        dists  = np.array(
            [np.linalg.norm(X - c, axis=1) for c in self._model.cluster_centers_]
        ).T                                   # (n_samples, k)
        probs  = np.exp(-dists)
        probs /= probs.sum(axis=1, keepdims=True)
        return states, probs
