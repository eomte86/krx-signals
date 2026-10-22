# krx-signals

Rules-based technical analysis signals for Korean equities (KOSPI / KOSDAQ).

한국 주식(KOSPI·KOSDAQ) 데이터를 위한 규칙 기반 기술적 분석 시그널 라이브러리입니다.

## Why this exists

Most technical-analysis libraries are market-agnostic. `krx-signals` is
opinionated for Korean equities: it pairs pure-pandas indicators
(no TA-Lib dependency) with a small, explainable rules engine —
moving-average crosses, RSI zones, MACD flips — verified against trading
volume. Every signal is a *technical observation*, never a recommendation.

기술적 분석 라이브러리 대부분은 시장에 구애받지 않게 설계되어 있습니다.
`krx-signals`는 한국 주식에 특화되어 있습니다: TA-Lib 없이 순수 pandas로
동작하는 지표 + 이동평균 크로스·RSI 구간·MACD 전환을 거래량 검증과 결합한
작은 규칙 엔진을 제공합니다. 모든 시그널은 *기술적 관찰*이며, 매수·매도
추천이 아닙니다.

> **Disclaimer / 면책:** This library is for research and education only.
> It is not investment advice. 모든 출력은 리서치·교육 목적이며 투자 조언이
> 아닙니다.

## Install

```bash
pip install krx-signals
# with KRX data fetching (pykrx)
pip install "krx-signals[krx]"
```

## Quickstart

```python
import pandas as pd
from krx_signals import generate_signals, describe_signals
from krx_signals.data import fetch_ohlcv

# 1) OHLCV 가져오기 (pykrx 필요)
df = fetch_ohlcv("005930", "20250101", "20261022", market="KOSPI")

# 2) 시그널 생성
sig = generate_signals(df)

# 3) 최근 발동 이벤트를 쉬운 말로 설명
for line in describe_signals(sig, lang="ko"):
    print(line)
```

`generate_signals` adds indicator columns (`ma_fast`, `ma_slow`, `rsi`,
`macd`, `macd_signal`, `macd_hist`, `volume_ma`), boolean event flags
(`golden_cross`, `death_cross`, `rsi_overbought`, `rsi_oversold`,
`macd_bullish`, `macd_bearish`, `volume_surge`), and two volume-verified
composites: `bullish_verified` (golden cross + volume surge) and
`bearish_verified` (death cross + volume surge).

## Indicators

| Function | Description |
|---|---|
| `sma / ema` | Simple / exponential moving average |
| `rsi` | Wilder's RSI (0–100) |
| `macd` | MACD line, signal line, histogram |
| `bollinger_bands` | Upper / middle / lower bands |
| `atr` | Average True Range (Wilder's) |
| `obv` | On-Balance Volume |

## Maintainer workflow

This project is maintained with an AI-assisted workflow (see
[docs/maintainer-workflow.md](docs/maintainer-workflow.md)): automated PR
review, release-note drafting, and issue triage. See [AGENTS.md](AGENTS.md)
for agent instructions and [CONTRIBUTING.md](CONTRIBUTING.md) to contribute.

## License

MIT — see [LICENSE](LICENSE).
