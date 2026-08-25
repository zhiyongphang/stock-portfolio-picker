import json
from pathlib import Path

PORTFOLIO_PATH = Path(__file__).resolve().parent.parent / "portfolio.json"
WATCHLIST_PATH = Path(__file__).resolve().parent.parent / "watchlist.json"


def load_portfolio() -> dict:
    return json.loads(PORTFOLIO_PATH.read_text())


def save_portfolio(portfolio: dict) -> None:
    PORTFOLIO_PATH.write_text(json.dumps(portfolio, indent=2))


def load_watchlist() -> list[str]:
    return json.loads(WATCHLIST_PATH.read_text())["tickers"]


def save_watchlist(tickers: list[str]) -> None:
    WATCHLIST_PATH.write_text(json.dumps({"tickers": tickers}, indent=2))


def add_holding(ticker: str, shares: float, cost_basis: float | None = None) -> None:
    portfolio = load_portfolio()
    ticker = ticker.strip().upper()
    holdings = portfolio.setdefault("holdings", [])
    for h in holdings:
        if h["ticker"] == ticker:
            h["shares"] = shares
            if cost_basis is not None:
                h["cost_basis"] = cost_basis
            save_portfolio(portfolio)
            return
    entry = {"ticker": ticker, "shares": shares}
    if cost_basis is not None:
        entry["cost_basis"] = cost_basis
    holdings.append(entry)
    save_portfolio(portfolio)


def remove_holding(ticker: str) -> None:
    portfolio = load_portfolio()
    portfolio["holdings"] = [h for h in portfolio.get("holdings", []) if h["ticker"] != ticker]
    save_portfolio(portfolio)


def set_cash(cash: float) -> None:
    portfolio = load_portfolio()
    portfolio["cash"] = cash
    save_portfolio(portfolio)
