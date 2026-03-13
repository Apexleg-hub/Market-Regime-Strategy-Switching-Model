"""models/kmeans_detector.py - K-Means clustering detector"""
from __future__ import annotations
import numpy as np
from typing import Tuple
from .base import BaseRegimeDetector

class KMeansDetector(BaseRegimeDetector):
    def __init__(self, n_states=5, n_init=20, random_state=42):
        super().__init__(n_states=n_states, random_state=random_state)
        self.n_init = n_init

    def _fit_predict(self, Xs: np.ndarray) -> Tuple[np.ndarray, np.ndarray, object]:
        from sklearn.cluster import KMeans
        model  = KMeans(n_clusters=self.n_states, n_init=self.n_init, random_state=self.random_state)
        labels = model.fit_predict(Xs)
        dists  = np.array([np.linalg.norm(Xs - c, axis=1) for c in model.cluster_centers_]).T
        probs  = np.exp(-dists); probs /= probs.sum(axis=1, keepdims=True)
        return labels, probs, model
