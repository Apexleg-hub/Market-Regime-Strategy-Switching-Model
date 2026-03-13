"""
models/factory.py
─────────────────
Factory function that returns the correct detector instance
based on the user's model_type string from the sidebar.
"""

from __future__ import annotations

from .base        import BaseRegimeModel
from .hmm_model   import HMMRegimeModel
from .gmm_model   import GMMRegimeModel
from .kmeans_model import KMeansRegimeModel


def get_model(model_type: str, n_states: int = 5) -> BaseRegimeModel:
    """
    Parameters
    ----------
    model_type : one of the strings in config.MODEL_OPTIONS
    n_states   : number of latent states / clusters

    Returns
    -------
    Instantiated (unfitted) BaseRegimeModel subclass
    """
    key = model_type.upper()
    if "HMM" in key or "MARKOV" in key:
        return HMMRegimeModel(n_states=n_states)
    elif "GMM" in key or "GAUSSIAN MIXTURE" in key or "MIXTURE" in key:
        return GMMRegimeModel(n_states=n_states)
    elif "KMEANS" in key or "K-MEANS" in key or "CLUSTER" in key:
        return KMeansRegimeModel(n_states=n_states)
    else:
        raise ValueError(f"Unknown model type: '{model_type}'. "
                         f"Choose from: HMM, GMM, K-Means.")
