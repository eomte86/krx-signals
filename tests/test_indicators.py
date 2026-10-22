"""Tests for krx_signals.indicators — deterministic, no network."""

import numpy as np
import pandas as pd
import pytest

from krx_signals.indicators import sma, ema, rsi, macd, bollinger_bands, atr, obv


def test_sma_known_values():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    out = sma(s, 3)
    assert out.isna().sum() == 2
    assert out.iloc[2] == pytest.approx(2.0)
    assert out.iloc[4] == pytest.approx(4.0)


def test_sma_invalid_window():
    with pytest.raises(ValueError):
        sma(pd.Series([1.0]), 0)


def test_ema_first_value_equals_first_close():
    s = pd.Series([10.0, 11.0, 12.0, 13.0])
    out = ema(s, 3)
    assert out.isna().sum() == 2  # min_periods=window
    # adjust=False: ema[2] = 12*0.5 + 11*0.25 + 10*0.25
    assert out.iloc[2] == pytest.approx(11.25)


def test_rsi_bounds_and_monotonic():
    up = pd.Series(np.arange(1.0, 51.0))
    assert rsi(up).iloc[-1] > 90
    down = pd.Series(np.arange(50.0, 0.0, -1.0))
    assert rsi(down).iloc[-1] < 10
    flat = pd.Series([5.0] * 40)
    assert rsi(flat).iloc[-1] == pytest.approx(50.0)
    assert ((rsi(up).dropna() >= 0) & (rsi(up).dropna() <= 100)).all()


def test_macd_columns_and_hist_identity():
    s = pd.Series(np.linspace(10, 20, 60))
    m = macd(s)
    assert list(m.columns) == ["macd", "signal", "hist"]
    assert np.allclose(m["hist"].dropna(), (m["macd"] - m["signal"]).dropna())


def test_macd_invalid_params():
    with pytest.raises(ValueError):
        macd(pd.Series([1.0, 2.0]), fast=26, slow=12)


def test_bollinger_ordering():
    s = pd.Series(np.linspace(10, 20, 60) + np.sin(np.linspace(0, 9, 60)))
    b = bollinger_bands(s)
    valid = b.dropna()
    assert (valid["upper"] >= valid["middle"]).all()
    assert (valid["middle"] >= valid["lower"]).all()


def test_atr_nonnegative():
    n = 40
    high = pd.Series(np.linspace(10, 15, n))
    low = high - 1.0
    close = (high + low) / 2
    a = atr(high, low, close)
    assert (a.dropna() >= 0).all()


def test_obv_direction():
    close = pd.Series([1.0, 2.0, 3.0, 2.0])
    vol = pd.Series([10.0, 10.0, 10.0, 10.0])
    o = obv(close, vol)
    assert o.iloc[-1] == pytest.approx(10.0)  # +10+10-10
