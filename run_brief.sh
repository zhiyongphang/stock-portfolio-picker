#!/bin/bash
set -euo pipefail
cd "/Users/zhiyong/Stock Portfolio Picker"
source .venv/bin/activate

mkdir -p briefs
OUT="briefs/$(date +%Y-%m-%d).txt"
python main.py brief > "$OUT" 2>&1 || true
python -m src.dashboard briefs/dashboard.html > /dev/null 2>&1 || true

SUMMARY=$(head -3 "$OUT")
osascript -e "display notification \"$(echo "$SUMMARY" | sed 's/"/\\"/g' | tr '\n' ' ')\" with title \"Portfolio Morning Brief\" subtitle \"Saved to $OUT\""
