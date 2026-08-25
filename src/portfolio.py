import json
from pathlib import Path

PORTFOLIO_PATH = Path(__file__).resolve().parent.parent / "portfolio.json"
WATCHLIST_PATH = Path(__file__).resolve().parent.parent / "watchlist.json"


def load_portfolio() -> dict:
    return json.loads(PORTFOLIO_PATH.read_text())


def load_watchlist() -> list[str]:
    return json.loads(WATCHLIST_PATH.read_text())["tickers"]
