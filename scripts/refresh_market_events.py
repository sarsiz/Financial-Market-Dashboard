#!/usr/bin/env python3
"""Refresh source-labeled market events into the local SQLite store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

import server  # noqa: E402


def main() -> int:
  parser = argparse.ArgumentParser(description="Refresh market-moving news/events into financial_board.db")
  parser.add_argument("--category", default="markets", help="Event category to refresh: markets, business, all, world, deals, etc.")
  parser.add_argument("--symbol", default="", help="Optional ticker symbol to tag and bias the event scan.")
  parser.add_argument("--query", default="", help="Optional explicit event/news query.")
  parser.add_argument("--limit", type=int, default=10, help="Number of stored rows to echo after refresh.")
  args = parser.parse_args()

  payload = server.build_event_feed(args.category, args.symbol.strip().upper() or None, args.query.strip() or None)
  stored = server.load_market_events(args.category, args.symbol.strip().upper() or None, limit=max(1, args.limit))
  print(json.dumps({
    "category": payload.get("category"),
    "query": payload.get("query"),
    "brief": payload.get("brief"),
    "stored": payload.get("localStore", {}),
    "items": stored,
  }, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
