from __future__ import annotations
import json, os
from typing import List

PATH = os.path.expanduser("~/.finance-dashboard.json")

def load_watchlist() -> List[str]:
    if not os.path.exists(PATH):
        return []
    try:
        with open(PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("tickers", [])
    except Exception:
        return []

def save_watchlist(tickers: List[str]) -> None:
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    clean = sorted(set([t.upper().strip() for t in tickers if t.strip()]))
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump({"tickers": clean}, f, indent=2)