# Market Regime + Strategy Switching Model

Streamlit application for detecting market regimes and dynamically switching
trading strategies — built as a clean, modular Python project.

## Project Structure

```
regime_switching/
│
├── app.py                     # Entry point — streamlit run app.py
├── requirements.txt
│
├── config/
│   ├── constants.py           # Regime definitions, feature cols, Plotly theme
│   └── settings.py            # AppSettings dataclass (sidebar → settings)
│
├── data/
│   └── loader.py              # load_ohlcv() — reads pkl or generates synthetic
│
├── features/
│   └── engineer.py            # engineer_features() — all indicator logic
│
├── models/
│   ├── base.py                # BaseRegimeModel ABC
│   ├── hmm_model.py           # GaussianHMM wrapper
│   ├── gmm_model.py           # GaussianMixture wrapper
│   ├── kmeans_model.py        # KMeans + soft assignment
│   ├── regime_mapper.py       # map_to_semantic_regimes()
│   └── factory.py             # get_model(model_type, n_states)
│
├── strategy/
│   └── signals.py             # generate_signals() — regime → signal
│
├── backtest/
│   └── engine.py              # run_backtest() → BacktestResult
│
├── utils/
│   └── scaler.py              # scale_features()
│
└── ui/
    ├── theme.py               # inject_css()
    ├── sidebar.py             # render_sidebar() → AppSettings
    ├── components.py          # HTML building blocks
    ├── charts.py              # All Plotly figure builders
    └── tabs.py                # render_price_tab / probability / equity / features
```

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Connecting Real MT5 Data

Place pkl files in  `data/cleaned/`  following the naming convention:

```
data/cleaned/EURUSD_H4.pkl
data/cleaned/GBPUSD_D1.pkl
data/cleaned/USDJPY_WK.pkl
```

The loader will automatically use real data when the file exists,
falling back to synthetic data otherwise.

## Regimes & Strategies

| Regime           | Strategy                      |
|------------------|-------------------------------|
| Bull Trend       | Moving Average / Momentum     |
| Bear Trend       | Inverse Momentum / Short MA   |
| High Volatility  | Breakout / Vol Expansion      |
| Low Volatility   | Carry Trade / Range Scalp     |
| Range Market     | Mean Reversion / Oscillator   |

## Models

| Algorithm | Class            | Notes                              |
|-----------|------------------|------------------------------------|
| HMM       | HMMRegimeModel   | Temporal persistence, Markov chain |
| GMM       | GMMRegimeModel   | Independent bar classification     |
| K-Means   | KMeansRegimeModel| Hard clusters + soft assignment    |
