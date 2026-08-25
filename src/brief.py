"""Assemble the full analysis for portfolio holdings + watchlist tickers."""
from . import data, indicators, valuation, news, strategy
from .portfolio import load_portfolio, load_watchlist


def analyze_ticker(ticker: str, position: dict | None = None) -> dict:
    quote = data.get_quote(ticker)
    hist = data.get_history(ticker, period="1y")
    if hist.empty:
        return {"ticker": ticker, "error": "No price data available"}

    info = data.get_info(ticker)
    tech = indicators.compute_all(hist)
    val = valuation.valuation_snapshot(info, tech)
    headlines = data.get_news(ticker, limit=5)
    sentiment = news.news_sentiment(headlines)
    signal = strategy.generate_signal(tech, val, sentiment, position=position)

    return {
        "ticker": ticker,
        "quote": quote,
        "tech": tech,
        "valuation": val,
        "sentiment": sentiment,
        "signal": signal,
        "position": position,
    }


def build_brief() -> dict:
    portfolio = load_portfolio()
    watchlist = load_watchlist()

    holdings_analysis = []
    for h in portfolio.get("holdings", []):
        ticker = h["ticker"]
        try:
            result = analyze_ticker(ticker)
            price = (result.get("quote") or {}).get("price")
            if price and h.get("cost_basis"):
                gain_pct = (price - h["cost_basis"]) / h["cost_basis"] * 100
                position = {
                    "shares": h["shares"],
                    "cost_basis": h["cost_basis"],
                    "market_value": price * h["shares"],
                    "gain_pct": gain_pct,
                }
                result = analyze_ticker(ticker, position=position)
            holdings_analysis.append(result)
        except Exception as e:
            holdings_analysis.append({"ticker": ticker, "error": str(e)})

    watchlist_analysis = []
    for ticker in watchlist:
        try:
            watchlist_analysis.append(analyze_ticker(ticker))
        except Exception as e:
            watchlist_analysis.append({"ticker": ticker, "error": str(e)})

    total_value = sum(
        (a.get("position") or {}).get("market_value", 0) for a in holdings_analysis
    ) + portfolio.get("cash", 0)

    undervalued_picks = [
        w for w in watchlist_analysis
        if not w.get("error") and w.get("valuation", {}).get("label") == "Undervalued"
    ]

    return {
        "cash": portfolio.get("cash", 0),
        "total_value": total_value,
        "holdings": holdings_analysis,
        "watchlist": watchlist_analysis,
        "undervalued_picks": undervalued_picks,
    }
