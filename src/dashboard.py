"""Render the brief dict as a static HTML dashboard."""
import html
import json
from datetime import datetime, timezone

ACTION_CLASS = {
    "BUY / ADD": "buy",
    "SELL / TRIM": "sell",
    "HOLD / WATCH": "hold",
}

VAL_CLASS = {
    "Undervalued": "buy",
    "Fairly valued": "hold",
    "No strong value signal": "muted",
}


def _e(s):
    return html.escape(str(s)) if s is not None else ""


def _fmt_money(x):
    return f"${x:,.2f}" if x is not None else "n/a"


def _fmt_pct(x):
    return f"{x:+.1f}%" if x is not None else "n/a"


def _ticker_card(a: dict, interactive: bool = False) -> str:
    tag = "form" if interactive else "article"
    tag_attrs = f' method="post" action="/holdings/remove/{_e(a["ticker"])}"' if interactive else ""
    remove_btn = (
        f'<button class="remove-btn" type="submit" title="Remove {_e(a["ticker"])}">&times;</button>'
        if interactive else ""
    )

    if a.get("error"):
        return f"""
        <{tag} class="card card--error"{tag_attrs}>
          <div class="card__head"><span class="ticker">{_e(a['ticker'])}</span>{remove_btn}</div>
          <p class="error">Data unavailable: {_e(a['error'])}</p>
        </{tag}>"""

    q, tech, val, sig, pos = a["quote"], a["tech"], a["valuation"], a["signal"], a.get("position")
    action_cls = ACTION_CLASS.get(sig["action"], "muted")
    val_cls = VAL_CLASS.get(val["label"], "muted")
    change_cls = "up" if (q["change_pct"] or 0) >= 0 else "down"

    position_html = ""
    if pos:
        position_html = f"""
          <div class="position">
            <span>{pos['shares']} sh @ {_fmt_money(pos['cost_basis'])}</span>
            <span>value {_fmt_money(pos['market_value'])}</span>
            <span class="{'up' if pos['gain_pct'] >= 0 else 'down'}">{_fmt_pct(pos['gain_pct'])} P/L</span>
          </div>"""

    reasons = "".join(f"<li class='reason reason--up'>{_e(b)}</li>" for b in sig["bullish"])
    reasons += "".join(f"<li class='reason reason--down'>{_e(b)}</li>" for b in sig["bearish"])

    return f"""
    <{tag} class="card"{tag_attrs}>
      <div class="card__head">
        <div>
          <span class="ticker">{_e(a['ticker'])}</span>
          <span class="name">{_e(q['name'])}</span>
        </div>
        <span class="pill pill--{action_cls}">{_e(sig['action'])}</span>
        {remove_btn}
      </div>
      <div class="price-row">
        <span class="price">{_fmt_money(q['price'])}</span>
        <span class="change {change_cls}">{_fmt_pct(q['change_pct'])} today</span>
        <span class="tag tag--{val_cls}">{_e(val['label'])}</span>
      </div>
      {position_html}
      <dl class="stats">
        <div><dt>RSI(14)</dt><dd>{tech['rsi14']:.0f}</dd></div>
        <div><dt>50/200 SMA</dt><dd>{'Golden' if tech['golden_cross'] else 'Death'} cross</dd></div>
        <div><dt>vs 52w high</dt><dd>{_fmt_pct(tech['pct_from_52w_high'])}</dd></div>
        <div><dt>Sentiment</dt><dd>{_e(a['sentiment']['label'])}</dd></div>
      </dl>
      <ul class="reasons">{reasons}</ul>
    </{tag}>"""


def render_html(brief: dict, interactive: bool = False) -> str:
    holdings = brief["holdings"]
    watchlist = brief["watchlist"]
    picks = brief["undervalued_picks"]

    counts = {"buy": 0, "sell": 0, "hold": 0}
    for a in holdings + watchlist:
        if a.get("error"):
            continue
        counts[ACTION_CLASS.get(a["signal"]["action"], "hold")] += 1

    generated = datetime.now(timezone.utc).strftime("%a %d %b %Y, %H:%M UTC")

    holdings_html = "".join(_ticker_card(a, interactive) for a in holdings)
    watchlist_html = "".join(_ticker_card(a, interactive) for a in watchlist)
    watchlist_section = ""
    if watchlist:
        watchlist_section = f"""
    <section class="section">
      <h2>Watchlist</h2>
      <div class="grid">{watchlist_html}</div>
    </section>"""

    toolbar_html = ""
    add_form_html = ""
    if interactive:
        toolbar_html = """
      <form method="post" action="/refresh"><button class="btn btn--refresh" type="submit">&#8635; Refresh</button></form>"""
        add_form_html = """
    <section class="section section--add">
      <h2>Add holding</h2>
      <form method="post" action="/holdings/add" class="add-form">
        <label>Ticker <input name="ticker" placeholder="e.g. CBA.AX" required></label>
        <label>Shares <input name="shares" type="number" step="any" min="0" required></label>
        <label>Cost basis (optional) <input name="cost_basis" type="number" step="any" min="0" placeholder="price paid"></label>
        <button class="btn btn--add" type="submit">Add / update</button>
      </form>
    </section>"""

    picks_html = ""
    if picks:
        items = "".join(
            f"<li><strong>{_e(p['ticker'])}</strong> — {_e(', '.join(p['valuation']['reasons']))}</li>"
            for p in picks
        )
        picks_html = f"""
    <section class="section section--picks">
      <h2>Undervalued picks</h2>
      <ul class="picks">{items}</ul>
    </section>"""

    return f"""<title>Portfolio Morning Brief</title>
<style>
:root {{
  --bg: #f5f3ee;
  --surface: #ffffff;
  --surface-alt: #ececE4;
  --ink: #1c2321;
  --muted: #62675f;
  --border: #ddd9cf;
  --accent: #2f6f5e;
  --accent-soft: #e4efec;
  --good: #2f7d4f;
  --good-soft: #e5f2e9;
  --warn: #9a6a26;
  --warn-soft: #f5ecdc;
  --bad: #a13a2b;
  --bad-soft: #f6e6e2;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #12151a;
    --surface: #1a1f26;
    --surface-alt: #212832;
    --ink: #e7e5df;
    --muted: #9aa0a6;
    --border: #2b323c;
    --accent: #6cbaa3;
    --accent-soft: #1c2c28;
    --good: #57b47c;
    --good-soft: #17281d;
    --warn: #d6a75a;
    --warn-soft: #2c2417;
    --bad: #dd7862;
    --bad-soft: #2e1c18;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #12151a;
  --surface: #1a1f26;
  --surface-alt: #212832;
  --ink: #e7e5df;
  --muted: #9aa0a6;
  --border: #2b323c;
  --accent: #6cbaa3;
  --accent-soft: #1c2c28;
  --good: #57b47c;
  --good-soft: #17281d;
  --warn: #d6a75a;
  --warn-soft: #2c2417;
  --bad: #dd7862;
  --bad-soft: #2e1c18;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
  line-height: 1.5;
}}
.wrap {{ max-width: 1080px; margin: 0 auto; padding: 2.5rem 1.5rem 4rem; }}
header.top {{
  display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between;
  gap: 0.75rem; margin-bottom: 0.5rem;
}}
h1 {{
  font-family: ui-serif, Georgia, "Iowan Old Style", serif;
  font-size: 2rem; font-weight: 600; margin: 0; text-wrap: balance;
  letter-spacing: -0.01em;
}}
.timestamp {{ color: var(--muted); font-size: 0.85rem; font-variant-numeric: tabular-nums; }}
.header-right {{ display: flex; align-items: center; gap: 0.9rem; }}
.disclaimer {{
  color: var(--muted); font-size: 0.85rem; margin: 0 0 2rem;
  border-left: 3px solid var(--border); padding-left: 0.75rem;
}}
.summary-bar {{
  display: flex; gap: 0.75rem; margin-bottom: 2.5rem; flex-wrap: wrap;
}}
.summary-chip {{
  flex: 1 1 140px; background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 0.9rem 1.1rem;
}}
.summary-chip .num {{
  font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 1.6rem;
  font-variant-numeric: tabular-nums; display: block;
}}
.summary-chip .label {{
  color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em;
}}
.summary-chip--buy .num {{ color: var(--good); }}
.summary-chip--sell .num {{ color: var(--bad); }}
.summary-chip--hold .num {{ color: var(--warn); }}
h2 {{
  font-family: ui-serif, Georgia, serif; font-size: 1.25rem; font-weight: 600;
  margin: 0 0 1rem; padding-top: 0.5rem; border-top: 1px solid var(--border);
}}
.section {{ margin-bottom: 2.5rem; }}
.grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;
}}
.card {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
  padding: 1.1rem 1.2rem; display: flex; flex-direction: column; gap: 0.7rem;
}}
.card--error {{ opacity: 0.7; }}
.error {{ color: var(--bad); font-size: 0.9rem; margin: 0; }}
.card__head {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }}
.ticker {{
  font-family: ui-monospace, "SF Mono", Menlo, monospace; font-weight: 700; font-size: 1.05rem;
  display: block;
}}
.name {{ color: var(--muted); font-size: 0.8rem; }}
.pill {{
  font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em;
  padding: 0.25rem 0.55rem; border-radius: 999px; white-space: nowrap;
}}
.pill--buy {{ background: var(--good-soft); color: var(--good); }}
.pill--sell {{ background: var(--bad-soft); color: var(--bad); }}
.pill--hold {{ background: var(--warn-soft); color: var(--warn); }}
.price-row {{ display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }}
.price {{
  font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 1.3rem; font-weight: 600;
  font-variant-numeric: tabular-nums;
}}
.change {{ font-size: 0.85rem; font-variant-numeric: tabular-nums; }}
.change.up {{ color: var(--good); }}
.change.down {{ color: var(--bad); }}
.tag {{
  font-size: 0.72rem; padding: 0.15rem 0.5rem; border-radius: 6px; margin-left: auto;
}}
.tag--buy {{ background: var(--good-soft); color: var(--good); }}
.tag--hold {{ background: var(--warn-soft); color: var(--warn); }}
.tag--muted {{ background: var(--surface-alt); color: var(--muted); }}
.position {{
  display: flex; gap: 0.75rem; flex-wrap: wrap; font-size: 0.82rem; color: var(--muted);
  font-variant-numeric: tabular-nums;
}}
.stats {{
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.4rem 0.8rem; margin: 0;
  padding: 0.6rem 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
}}
.stats div {{ display: flex; justify-content: space-between; }}
.stats dt {{ color: var(--muted); font-size: 0.78rem; }}
.stats dd {{ margin: 0; font-size: 0.82rem; font-variant-numeric: tabular-nums; font-weight: 500; }}
ul.reasons {{ list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.35rem; }}
.reason {{ font-size: 0.82rem; padding-left: 1.1rem; position: relative; }}
.reason::before {{ position: absolute; left: 0; font-weight: 700; }}
.reason--up {{ color: var(--ink); }}
.reason--up::before {{ content: "+"; color: var(--good); }}
.reason--down {{ color: var(--ink); }}
.reason--down::before {{ content: "\\2212"; color: var(--bad); }}
.picks {{ margin: 0; padding-left: 1.2rem; }}
.picks li {{ margin-bottom: 0.4rem; font-size: 0.92rem; }}
footer {{ margin-top: 3rem; color: var(--muted); font-size: 0.78rem; }}
.btn {{
  font: inherit; font-size: 0.85rem; font-weight: 600; padding: 0.5rem 0.9rem;
  border-radius: 8px; border: 1px solid var(--border); background: var(--surface);
  color: var(--ink); cursor: pointer;
}}
.btn:hover {{ border-color: var(--accent); color: var(--accent); }}
.btn--add {{ background: var(--accent); color: var(--surface); border-color: var(--accent); }}
.btn--add:hover {{ opacity: 0.9; color: var(--surface); }}
.remove-btn {{
  background: none; border: none; color: var(--muted); font-size: 1.1rem; line-height: 1;
  cursor: pointer; padding: 0 0.2rem; margin-left: 0.3rem;
}}
.remove-btn:hover {{ color: var(--bad); }}
.add-form {{
  display: flex; flex-wrap: wrap; gap: 1rem; align-items: flex-end;
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem 1.2rem;
}}
.add-form label {{
  display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.78rem; color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.03em; flex: 1 1 160px;
}}
.add-form input {{
  font: inherit; font-size: 0.95rem; padding: 0.5rem 0.6rem; border-radius: 6px;
  border: 1px solid var(--border); background: var(--bg); color: var(--ink);
  font-variant-numeric: tabular-nums;
}}
</style>
<div class="wrap">
  <header class="top">
    <h1>Portfolio Morning Brief</h1>
    <div class="header-right">
      <span class="timestamp">Generated {generated}</span>
      {toolbar_html}
    </div>
  </header>
  <p class="disclaimer">Heuristic decision-support only, not financial advice — technicals, a basic valuation screen, and headline sentiment, combined into a signal for you to weigh yourself.</p>

  <div class="summary-bar">
    <div class="summary-chip summary-chip--buy"><span class="num">{counts['buy']}</span><span class="label">Buy / Add</span></div>
    <div class="summary-chip summary-chip--hold"><span class="num">{counts['hold']}</span><span class="label">Hold / Watch</span></div>
    <div class="summary-chip summary-chip--sell"><span class="num">{counts['sell']}</span><span class="label">Sell / Trim</span></div>
  </div>

  <section class="section">
    <h2>Holdings</h2>
    <div class="grid">{holdings_html}</div>
  </section>
  {watchlist_section}
  {add_form_html}
  {picks_html}
  <footer>Data via Yahoo Finance (yfinance). Sentiment is basic keyword scoring, not an NLP model.</footer>
</div>
"""


if __name__ == "__main__":
    import sys
    from .brief import build_brief
    out_path = sys.argv[1] if len(sys.argv) > 1 else "dashboard.html"
    with open(out_path, "w") as f:
        f.write(render_html(build_brief()))
    print(f"Wrote {out_path}")
