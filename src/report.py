"""Render the brief dict as plain text for terminal/chat output."""


def _fmt_pct(x):
    return f"{x:+.1f}%" if x is not None else "n/a"


def render_text(brief: dict) -> str:
    lines = []
    lines.append(f"PORTFOLIO SNAPSHOT — total value ${brief['total_value']:,.2f} (cash ${brief['cash']:,.2f})")
    lines.append("=" * 60)

    for h in brief["holdings"]:
        if h.get("error"):
            lines.append(f"\n{h['ticker']}: ERROR — {h['error']}")
            continue
        q, pos, sig, val = h["quote"], h["position"], h["signal"], h["valuation"]
        lines.append(
            f"\n{h['ticker']} ({q['name']})  ${q['price']:.2f}  {_fmt_pct(q['change_pct'])} today"
        )
        if pos:
            lines.append(
                f"  Position: {pos['shares']} sh, cost ${pos['cost_basis']:.2f}, "
                f"value ${pos['market_value']:,.2f}, P/L {_fmt_pct(pos['gain_pct'])}"
            )
        lines.append(f"  Signal: {sig['action']}  |  Valuation: {val['label']}")
        for b in sig["bullish"]:
            lines.append(f"    + {b}")
        for b in sig["bearish"]:
            lines.append(f"    - {b}")

    lines.append("\n" + "=" * 60)
    lines.append("WATCHLIST")
    for w in brief["watchlist"]:
        if w.get("error"):
            lines.append(f"\n{w['ticker']}: ERROR — {w['error']}")
            continue
        q, sig, val = w["quote"], w["signal"], w["valuation"]
        lines.append(
            f"\n{w['ticker']} ({q['name']})  ${q['price']:.2f}  {_fmt_pct(q['change_pct'])} today  "
            f"— {sig['action']}  |  {val['label']}"
        )

    if brief["undervalued_picks"]:
        lines.append("\n" + "=" * 60)
        lines.append("UNDERVALUED PICKS THIS RUN:")
        for p in brief["undervalued_picks"]:
            lines.append(f"  {p['ticker']}: {', '.join(p['valuation']['reasons'])}")

    return "\n".join(lines)
