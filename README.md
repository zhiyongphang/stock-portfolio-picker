# Stock Portfolio Picker

Your personal fund-manager assistant: tracks your portfolio, screens your watchlist
for undervalued stocks using technical + valuation + news signals, and produces
a morning brief.

**Not financial advice** — this is a heuristic decision-support tool. It surfaces
signals for you to weigh; you make the calls.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure

- `portfolio.json` — your holdings (`ticker`, `shares`, `cost_basis`) and cash.
- `watchlist.json` — tickers you want screened for buy opportunities.

## Run

```bash
source .venv/bin/activate
python main.py brief   # human-readable summary
python main.py json    # raw structured data
```

## What it looks at per ticker

- **Technicals**: 50/200-day SMA (golden/death cross), RSI(14), MACD, Bollinger
  Bands, distance from 52-week high/low.
- **Valuation**: trailing vs. forward P/E, PEG ratio, price/book, discount from
  52-week high, oversold RSI — combined into an Undervalued / Fairly valued /
  No signal label.
- **News**: latest headlines per ticker with lightweight keyword sentiment.
- **Strategy**: combines the above (and your cost basis / gain % for holdings
  you already own) into a BUY/ADD, SELL/TRIM, or HOLD/WATCH signal with the
  bullish/bearish reasons listed out.

## Morning brief automation

This is set up to run automatically via a Claude scheduled task each weekday
morning and message you the results. See the `schedule` skill / Claude Code
scheduled tasks to view or change the time.

## Data sources

All free/public: Yahoo Finance via `yfinance` for prices, fundamentals, and
headlines. No API key required. Swap in a paid data/news provider later by
editing `src/data.py` and `src/news.py`.
