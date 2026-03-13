"""
models/base.py
──────────────
Abstract base class that every regime detection model must implement.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np


class BaseRegimeModel(ABC):
    """Common interface for HMM, GMM, and K-Means regime detectors."""

    def __init__(self, n_states: int = 5, random_state: int = 42):
        self.n_states     = n_states
        self.random_state = random_state
        self._model       = None

    @abstractmethod
    def fit_predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Fit on scaled feature matrix X, return (states, probs)."""

    @property
    def model(self):
        return self._model

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(n_states={self.n_states})"
