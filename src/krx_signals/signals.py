"""Rules-based signal layer.

Combines the indicators in :mod:`krx_signals.indicators` into discrete,
explainable technical events, with volume verification filters.

These are *technical observations*, not investment advice. Every event
describes what happened in the price/volume data — never a buy/sell
recommendation. See the module disclaimer in the README.
"""

from __future__ import annotations

import pandas as pd

from krx_signals.indicators import sma, rsi, macd


def _require_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    missing = {"close", "volume"} - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame must contain columns {sorted(missing)}")
    return df


def golden_cross(df: pd.DataFrame, fast: int = 5, slow: int = 20) -> pd.Series:
    """True where the fast MA crosses *above* the slow MA."""
    df = _require_ohlcv(df)
    f, s = sma(df["close"], fast), sma(df["close"], slow)
    return (f > s) & (f.shift(1) <= s.shift(1))


def death_cross(df: pd.DataFrame, fast: int = 5, slow: int = 20) -> pd.Series:
    """True where the fast MA crosses *below* the slow MA."""
    df = _require_ohlcv(df)
    f, s = sma(df["close"], fast), sma(df["close"], slow)
    return (f < s) & (f.shift(1) >= s.shift(1))


def rsi_overbought(close: pd.Series, window: int = 14, level: float = 70) -> pd.Series:
    """True where RSI is at or above the overbought level."""
    return rsi(close, window) >= level


def rsi_oversold(close: pd.Series, window: int = 14, level: float = 30) -> pd.Series:
    """True where RSI is at or below the oversold level."""
    return rsi(close, window) <= level


def macd_bullish_flip(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.Series:
    """True where the MACD histogram flips from <= 0 to > 0."""
    hist = macd(close, fast, slow, signal)["hist"]
    return (hist > 0) & (hist.shift(1) <= 0)


def macd_bearish_flip(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.Series:
    """True where the MACD histogram flips from >= 0 to < 0."""
    hist = macd(close, fast, slow, signal)["hist"]
    return (hist < 0) & (hist.shift(1) >= 0)


def volume_surge(df: pd.DataFrame, window: int = 20, multiple: float = 1.5) -> pd.Series:
    """True where volume is at least ``multiple`` x its rolling mean.

    Used as a verification filter: a price signal accompanied by unusual
    volume is treated as more noteworthy than one on thin trading.
    """
    df = _require_ohlcv(df)
    avg = df["volume"].rolling(window=window, min_periods=window).mean()
    return df["volume"] >= multiple * avg


def generate_signals(
    df: pd.DataFrame,
    ma_fast: int = 5,
    ma_slow: int = 20,
    rsi_window: int = 14,
    volume_window: int = 20,
    volume_multiple: float = 1.5,
) -> pd.DataFrame:
    """Attach indicator values and event flags to an OHLCV DataFrame.

    Returns a copy of ``df`` with indicator columns
    (``ma_fast``, ``ma_slow``, ``rsi``, ``macd``, ``macd_signal``,
    ``macd_hist``, ``volume_ma``), boolean event columns, and two
    volume-verified composite flags:

    - ``bullish_verified``: golden cross confirmed by a volume surge
    - ``bearish_verified``: death cross confirmed by a volume surge
    """
    df = _require_ohlcv(df).copy()
    close = df["close"]

    df["ma_fast"] = sma(close, ma_fast)
    df["ma_slow"] = sma(close, ma_slow)
    df["rsi"] = rsi(close, rsi_window)
    m = macd(close)
    df["macd"], df["macd_signal"], df["macd_hist"] = m["macd"], m["signal"], m["hist"]
    df["volume_ma"] = df["volume"].rolling(volume_window, min_periods=volume_window).mean()

    df["golden_cross"] = golden_cross(df, ma_fast, ma_slow)
    df["death_cross"] = death_cross(df, ma_fast, ma_slow)
    df["rsi_overbought"] = rsi_overbought(close, rsi_window)
    df["rsi_oversold"] = rsi_oversold(close, rsi_window)
    df["macd_bullish"] = macd_bullish_flip(close)
    df["macd_bearish"] = macd_bearish_flip(close)
    df["volume_surge"] = volume_surge(df, volume_window, volume_multiple)

    df["bullish_verified"] = df["golden_cross"] & df["volume_surge"]
    df["bearish_verified"] = df["death_cross"] & df["volume_surge"]
    return df


def describe_signals(df: pd.DataFrame, lang: str = "ko") -> list[str]:
    """Describe the latest row's triggered events in plain language.

    Returns a list of human-readable sentences (Korean by default,
    ``lang="en"`` for English). Purely descriptive — which technical
    conditions triggered and whether volume verified them. Never a
    recommendation.
    """
    if df.empty:
        return []
    row = df.iloc[-1]
    date = df.index[-1]
    try:
        date_s = pd.Timestamp(date).strftime("%Y-%m-%d")
    except Exception:  # noqa: BLE001
        date_s = str(date)

    ko = lang == "ko"
    out: list[str] = []
    if bool(row.get("golden_cross")):
        out.append(
            f"{date_s}: 단기 이동평균선이 장기 이동평균선을 상향 돌파했습니다(골든크로스)."
            if ko
            else f"{date_s}: fast MA crossed above slow MA (golden cross)."
        )
    if bool(row.get("death_cross")):
        out.append(
            f"{date_s}: 단기 이동평균선이 장기 이동평균선을 하향 돌파했습니다(데드크로스)."
            if ko
            else f"{date_s}: fast MA crossed below slow MA (death cross)."
        )
    if bool(row.get("rsi_overbought")):
        out.append(
            f"{date_s}: RSI가 {row['rsi']:.1f}로 과매수 구간에 있습니다."
            if ko
            else f"{date_s}: RSI at {row['rsi']:.1f} (overbought zone)."
        )
    if bool(row.get("rsi_oversold")):
        out.append(
            f"{date_s}: RSI가 {row['rsi']:.1f}로 과매도 구간에 있습니다."
            if ko
            else f"{date_s}: RSI at {row['rsi']:.1f} (oversold zone)."
        )
    if bool(row.get("macd_bullish")):
        out.append(
            f"{date_s}: MACD 히스토그램이 양전환했습니다."
            if ko
            else f"{date_s}: MACD histogram turned positive."
        )
    if bool(row.get("macd_bearish")):
        out.append(
            f"{date_s}: MACD 히스토그램이 음전환했습니다."
            if ko
            else f"{date_s}: MACD histogram turned negative."
        )
    if bool(row.get("volume_surge")) and pd.notna(row.get("volume_ma")) and row["volume_ma"]:
        ratio = row["volume"] / row["volume_ma"]
        out.append(
            f"거래량은 20일 평균의 {ratio:.1f}배로 확인됐습니다."
            if ko
            else f"Volume is {ratio:.1f}x its 20-day average."
        )
    if not out:
        out.append(
            "특이 신호 없음: 주요 기술적 조건이 발동하지 않았습니다."
            if ko
            else "No notable signals: no major technical conditions triggered."
        )
    return out
