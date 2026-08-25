"""Simple valuation screen: is a stock cheap relative to its own history and fundamentals?"""


def valuation_snapshot(info: dict, tech: dict) -> dict:
    trailing_pe = info.get("trailingPE")
    forward_pe = info.get("forwardPE")
    peg = info.get("pegRatio")
    pb = info.get("priceToBook")

    score = 0
    reasons = []

    if forward_pe and trailing_pe and forward_pe < trailing_pe:
        score += 1
        reasons.append("Forward P/E below trailing P/E (earnings expected to grow)")

    if peg is not None and peg < 1.5:
        score += 1
        reasons.append(f"PEG ratio {peg:.2f} suggests reasonable price relative to growth")

    if tech.get("pct_from_52w_high") is not None and tech["pct_from_52w_high"] <= -20:
        score += 1
        reasons.append(f"Trading {tech['pct_from_52w_high']:.1f}% below its 52-week high")

    if tech.get("rsi14") is not None and tech["rsi14"] < 35:
        score += 1
        reasons.append(f"RSI at {tech['rsi14']:.0f} indicates oversold conditions")

    if pb is not None and pb < 3:
        score += 1
        reasons.append(f"Price/Book of {pb:.2f} is reasonable")

    label = "Undervalued" if score >= 3 else ("Fairly valued" if score == 2 else "No strong value signal")

    return {
        "trailing_pe": trailing_pe,
        "forward_pe": forward_pe,
        "peg": peg,
        "price_to_book": pb,
        "score": score,
        "label": label,
        "reasons": reasons,
    }
