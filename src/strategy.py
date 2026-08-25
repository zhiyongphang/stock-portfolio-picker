"""Combine technicals + valuation + news into a plain-English signal.

This is a heuristic decision-support tool, not financial advice. It surfaces
signals; the user makes the call.
"""


def generate_signal(tech: dict, val: dict, sentiment: dict, position: dict | None = None) -> dict:
    bullish, bearish = [], []

    if tech.get("golden_cross"):
        bullish.append("50-day SMA above 200-day SMA (golden cross / uptrend)")
    elif tech.get("sma50") and tech.get("sma200") and tech["sma50"] < tech["sma200"]:
        bearish.append("50-day SMA below 200-day SMA (death cross / downtrend)")

    rsi14 = tech.get("rsi14")
    if rsi14 is not None:
        if rsi14 < 30:
            bullish.append(f"RSI {rsi14:.0f}: oversold, potential bounce")
        elif rsi14 > 70:
            bearish.append(f"RSI {rsi14:.0f}: overbought, potential pullback")

    if tech.get("macd_hist") is not None:
        if tech["macd_hist"] > 0:
            bullish.append("MACD histogram positive (bullish momentum)")
        else:
            bearish.append("MACD histogram negative (bearish momentum)")

    if val.get("label") == "Undervalued":
        bullish.append("Valuation screen: undervalued vs. fundamentals/history")
    elif val.get("score", 0) == 0:
        bearish.append("Valuation screen: no discount found, may be pricey")

    if sentiment.get("label") == "Positive":
        bullish.append("Recent news sentiment leans positive")
    elif sentiment.get("label") == "Negative":
        bearish.append("Recent news sentiment leans negative")

    net = len(bullish) - len(bearish)

    if position:
        gain_pct = position.get("gain_pct")
        if gain_pct is not None and gain_pct >= 30 and rsi14 and rsi14 > 65:
            bearish.append(f"Up {gain_pct:.1f}% with RSI hot — consider trimming into strength")
        if gain_pct is not None and gain_pct <= -15:
            bullish.append(f"Down {gain_pct:.1f}% from cost basis — reassess thesis, potential add-on-dip if fundamentals intact")

    if net >= 2:
        action = "BUY / ADD"
    elif net <= -2:
        action = "SELL / TRIM"
    else:
        action = "HOLD / WATCH"

    return {
        "action": action,
        "net_score": net,
        "bullish": bullish,
        "bearish": bearish,
    }
