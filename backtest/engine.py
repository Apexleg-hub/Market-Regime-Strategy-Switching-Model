"""
backtest/engine.py
──────────────────
Vectorised backtest engine.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    equity:    pd.Series
    benchmark: pd.Series
    returns:   pd.Series
    metrics:   dict

    @property
    def total_return(self) -> float: return self.metrics["total"]
    @property
    def ann_return(self)   -> float: return self.metrics["ann"]
    @property
    def sharpe(self)       -> float: return self.metrics["sharpe"]
    @property
    def max_drawdown(self) -> float: return self.metrics["max_dd"]
    @property
    def ann_vol(self)      -> float: return self.metrics["vol"]


def run_backtest(df: pd.DataFrame, signals: pd.Series,
                 slippage: float = 0.00005) -> BacktestResult:
    ret          = df["ret_1"].copy()
    pos          = signals.shift(1).fillna(0)
    turnover     = np.abs(signals.diff().fillna(0))
    strategy_ret = pos * ret - turnover * slippage
    equity       = (1 + strategy_ret).cumprod()
    benchmark    = (1 + ret).cumprod()
    return BacktestResult(
        equity=equity, benchmark=benchmark, returns=strategy_ret,
        metrics=_metrics(strategy_ret, equity),
    )


def _metrics(returns: pd.Series, equity: pd.Series) -> dict:
    total   = equity.iloc[-1] - 1
    ann     = (1 + total) ** (252 / max(len(equity), 1)) - 1
    vol_ann = returns.std() * np.sqrt(252)
    sharpe  = ann / (vol_ann + 1e-10)
    max_dd  = (equity / equity.cummax() - 1).min()
    return {"total": total, "ann": ann, "sharpe": sharpe, "max_dd": max_dd, "vol": vol_ann}
