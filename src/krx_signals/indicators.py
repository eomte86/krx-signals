"""Pure-pandas technical indicators.

Implemented without TA-Lib so the library installs with only pandas/numpy.
All functions accept pandas Series and return the same index.

Conventions:
- ``close`` / ``high`` / ``low`` / ``volume`` are pandas Series.
- Moving averages use the standard definitions; RSI and ATR use Wilder's
  smoothing (alpha = 1/window), matching the most common references.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(close: pd.Series, window: int) -> pd.Series:
    """Simple moving average."""
    if window < 1:
        raise ValueError("window must be >= 1")
    return close.rolling(window=window, min_periods=window).mean()


def ema(close: pd.Series, window: int) -> pd.Series:
    """Exponential moving average (span=window, adjust=False)."""
    if window < 1:
        raise ValueError("window must be >= 1")
    return close.ewm(span=window, min_periods=window, adjust=False).mean()


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index with Wilder's smoothing, range [0, 100].

    Edge cases: pure gains -> 100, pure losses -> 0, flat series -> 50.
    """
    if window < 1:
        raise ValueError("window must be >= 1")
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    # Where average loss is zero: 100 if there were gains, else 50 (flat).
    out = out.where(avg_loss != 0, np.where(avg_gain != 0, 100.0, 50.0))
    return out


def macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.DataFrame:
    """MACD line, signal line and histogram."""
    if not (0 < fast < slow):
        raise ValueError("require 0 < fast < slow")
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return pd.DataFrame(
        {"macd": line, "signal": sig, "hist": line - sig}, index=close.index
    )


def bollinger_bands(
    close: pd.Series, window: int = 20, num_std: float = 2.0
) -> pd.DataFrame:
    """Bollinger Bands (upper / middle / lower)."""
    mid = sma(close, window)
    std = close.rolling(window=window, min_periods=window).std()
    return pd.DataFrame(
        {
            "upper": mid + num_std * std,
            "middle": mid,
            "lower": mid - num_std * std,
        },
        index=close.index,
    )


def atr(
    high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14
) -> pd.Series:
    """Average True Range with Wilder's smoothing."""
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume."""
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()
