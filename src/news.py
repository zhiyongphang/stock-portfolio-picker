"""Very lightweight headline sentiment via keyword scoring (no external API/model call)."""

POSITIVE_WORDS = {
    "beat", "beats", "surge", "soars", "upgrade", "upgraded", "record", "growth",
    "strong", "rally", "outperform", "bullish", "profit", "gains", "buyback",
    "expansion", "partnership", "wins", "approval", "raises",
}
NEGATIVE_WORDS = {
    "miss", "misses", "plunge", "downgrade", "downgraded", "lawsuit", "recall",
    "weak", "decline", "bearish", "loss", "layoffs", "investigation", "fraud",
    "cuts", "warns", "warning", "sell-off", "selloff", "delay",
}


def score_headline(title: str) -> int:
    t = title.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in t)
    neg = sum(1 for w in NEGATIVE_WORDS if w in t)
    return pos - neg


def news_sentiment(headlines: list[dict]) -> dict:
    if not headlines:
        return {"score": 0, "label": "No recent news", "headlines": []}
    scored = []
    total = 0
    for h in headlines:
        s = score_headline(h.get("title", ""))
        total += s
        scored.append({**h, "sentiment": s})
    label = "Positive" if total > 0 else ("Negative" if total < 0 else "Neutral")
    return {"score": total, "label": label, "headlines": scored}
