"""krx-signals: rules-based technical analysis signals for Korean equities."""

from krx_signals.indicators import (
    sma,
    ema,
    rsi,
    macd,
    bollinger_bands,
    atr,
    obv,
)
from krx_signals.signals import (
    golden_cross,
    death_cross,
    rsi_overbought,
    rsi_oversold,
    macd_bullish_flip,
    macd_bearish_flip,
    volume_surge,
    generate_signals,
    describe_signals,
)

__version__ = "0.1.0"
__all__ = [
    "sma",
    "ema",
    "rsi",
    "macd",
    "bollinger_bands",
    "atr",
    "obv",
    "golden_cross",
    "death_cross",
    "rsi_overbought",
    "rsi_oversold",
    "macd_bullish_flip",
    "macd_bearish_flip",
    "volume_surge",
    "generate_signals",
    "describe_signals",
]
