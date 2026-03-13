"""
config/settings.py
──────────────────
Runtime settings dataclass — populated from the Streamlit sidebar.
Can also be constructed directly for headless / script usage.
"""

from dataclasses import dataclass


@dataclass
class AppSettings:
    # Data
    symbol:        str   = "EURUSD"
    timeframe:     str   = "H4"
    n_bars:        int   = 500

    # Model
    model_type:    str   = "Hidden Markov Model (HMM)"
    n_states:      int   = 5

    # Execution
    slippage_bps:  float = 2.0

    @property
    def slippage(self) -> float:
        return self.slippage_bps / 10_000

    @property
    def model_short(self) -> str:
        return self.model_type.split()[0]
