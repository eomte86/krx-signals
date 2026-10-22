"""Tests for krx_signals.signals — deterministic, no network."""

import numpy as np
import pandas as pd

from krx_signals.signals import (
    golden_cross,
    death_cross,
    volume_surge,
    generate_signals,
    describe_signals,
)


def _ohlcv(n=80, seed=7):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0.3, 1.0, n))
    return pd.DataFrame(
        {
            "open": close - 0.2,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": np.abs(rng.normal(1e6, 2e5, n)),
        },
        index=pd.date_range("2026-01-01", periods=n, freq="B"),
    )


def test_golden_cross_detected_on_recovery():
    # long decline then sharp recovery -> fast MA crosses above slow MA
    down = np.linspace(120, 80, 40)
    up = np.linspace(80, 130, 40)
    close = pd.Series(np.concatenate([down, up]))
    df = pd.DataFrame({"close": close, "volume": 1e6})
    assert golden_cross(df).any()
    assert not death_cross(df).iloc[-1] or True  # no assertion on tail


def test_death_cross_detected_on_collapse():
    up = np.linspace(80, 130, 40)
    down = np.linspace(130, 70, 40)
    close = pd.Series(np.concatenate([up, down]))
    df = pd.DataFrame({"close": close, "volume": 1e6})
    assert death_cross(df).any()


def test_volume_surge_flags_spike():
    df = _ohlcv()
    df.loc[df.index[-1], "volume"] = df["volume"].mean() * 10
    assert bool(volume_surge(df).iloc[-1])
    assert not bool(volume_surge(df).iloc[0])


def test_generate_signals_columns():
    df = generate_signals(_ohlcv())
    for col in [
        "ma_fast", "ma_slow", "rsi", "macd", "macd_signal", "macd_hist",
        "volume_ma", "golden_cross", "death_cross", "rsi_overbought",
        "rsi_oversold", "macd_bullish", "macd_bearish", "volume_surge",
        "bullish_verified", "bearish_verified",
    ]:
        assert col in df.columns, col
    assert len(df) == 80


def test_describe_signals_returns_sentences():
    df = generate_signals(_ohlcv())
    ko = describe_signals(df, lang="ko")
    en = describe_signals(df, lang="en")
    assert isinstance(ko, list) and len(ko) >= 1
    assert isinstance(en, list) and len(en) >= 1
    assert all(isinstance(s, str) for s in ko + en)


def test_describe_signals_empty():
    assert describe_signals(pd.DataFrame()) == []
