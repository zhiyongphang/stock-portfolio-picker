"""Market data fetching via yfinance."""
import yfinance as yf
import pandas as pd


def get_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    return df


def get_info(ticker: str) -> dict:
    return yf.Ticker(ticker).info or {}


def get_news(ticker: str, limit: int = 5) -> list[dict]:
    try:
        items = yf.Ticker(ticker).news or []
    except Exception:
        items = []
    out = []
    for it in items[:limit]:
        c = it.get("content", it)
        out.append({
            "title": c.get("title") or it.get("title", ""),
            "publisher": (c.get("provider") or {}).get("displayName", "") if isinstance(c.get("provider"), dict) else it.get("publisher", ""),
            "link": (c.get("canonicalUrl") or {}).get("url", "") if isinstance(c.get("canonicalUrl"), dict) else it.get("link", ""),
        })
    return out


def get_quote(ticker: str) -> dict:
    info = get_info(ticker)
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    prev_close = info.get("previousClose")
    change_pct = None
    if price is not None and prev_close:
        change_pct = (price - prev_close) / prev_close * 100
    return {
        "ticker": ticker,
        "price": price,
        "prev_close": prev_close,
        "change_pct": change_pct,
        "name": info.get("shortName", ticker),
    }
