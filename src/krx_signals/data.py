"""Market data adapters.

The core library works on any OHLCV DataFrame. This module provides a
convenience adapter for KRX data via ``pykrx`` (optional dependency).
"""

from __future__ import annotations

import pandas as pd

_COLUMN_MAP = {
    "시가": "open",
    "고가": "high",
    "저가": "low",
    "종가": "close",
    "거래량": "volume",
    "거래대금": "amount",
}


def fetch_ohlcv(
    ticker: str,
    start: str,
    end: str,
    market: str = "KOSPI",
    adjusted: bool = False,
) -> pd.DataFrame:
    """Fetch daily OHLCV for a KRX ticker via pykrx.

    Parameters
    ----------
    ticker:
        6-digit ticker code, e.g. ``"005930"``.
    start, end:
        ``"YYYYMMDD"`` date strings.
    market:
        ``"KOSPI"``, ``"KOSDAQ"`` or ``"KONEX"``.
    adjusted:
        When True, use Naver Finance adjusted prices (splits/dividends).

    Returns a DataFrame indexed by date with ``open/high/low/close/volume``
    columns, ready for :func:`krx_signals.signals.generate_signals`.
    """
    try:
        from pykrx import stock
    except ImportError as exc:
        raise ImportError(
            "pykrx is required for fetch_ohlcv: pip install 'krx-signals[krx]'"
        ) from exc

    if adjusted:
        raw = stock.get_market_ohlcv_by_date(start, end, ticker, adjusted=True)
    else:
        raw = stock.get_market_ohlcv(start, end, ticker, market=market)
    df = raw.rename(columns=_COLUMN_MAP)
    df.index.name = "date"
    return df[["open", "high", "low", "close", "volume"]].copy()
