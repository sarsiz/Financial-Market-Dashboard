#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

import server


def load_universe(name: str) -> list[dict]:
  path = ROOT / "data" / "universes" / f"{name}.json"
  if not path.exists():
    raise SystemExit(f"Universe file not found: {path}")
  return json.loads(path.read_text())


def returns(values: list[float]) -> list[float]:
  output = []
  for index in range(1, len(values)):
    previous = values[index - 1]
    current = values[index]
    if previous:
      output.append((current - previous) / previous)
  return output


def correlation(left: list[float], right: list[float]) -> float:
  size = min(len(left), len(right))
  if size < 10:
    return 0.0
  left = left[-size:]
  right = right[-size:]
  left_mean = sum(left) / size
  right_mean = sum(right) / size
  numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
  left_var = sum((a - left_mean) ** 2 for a in left)
  right_var = sum((b - right_mean) ** 2 for b in right)
  denominator = math.sqrt(left_var * right_var)
  return (numerator / denominator) if denominator else 0.0


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--universe", required=True, help="sensex30 | sp500 | nasdaq_listed")
  parser.add_argument("--limit", type=int, default=0)
  parser.add_argument("--min-corr", type=float, default=0.55)
  args = parser.parse_args()

  members = load_universe(args.universe)
  if args.limit > 0:
    members = members[: args.limit]

  histories = {}
  for item in members:
    records = server.load_historical_records(item["symbol"], "1wk")
    closes = [point["value"] for point in records if isinstance(point.get("value"), (int, float))]
    if len(closes) < 20:
      cached = server.load_cached_history(item["symbol"], "1Y")
      if not cached:
        continue
      closes = cached[0]
    if len(closes) >= 20:
      histories[item["symbol"]] = returns(closes)

  nodes = [
    {
      "id": item["symbol"],
      "label": item.get("symbol"),
      "name": item.get("name", item.get("symbol")),
      "sector": item.get("sector", ""),
      "region": item.get("region", ""),
    }
    for item in members
    if item["symbol"] in histories
  ]

  links = []
  node_map = {item["symbol"]: item for item in members}
  symbols = list(histories.keys())
  for index, left_symbol in enumerate(symbols):
    for right_symbol in symbols[index + 1 :]:
      corr = correlation(histories[left_symbol], histories[right_symbol])
      if abs(corr) < args.min_corr:
        continue
      left_meta = node_map[left_symbol]
      right_meta = node_map[right_symbol]
      relation = "correlation"
      if left_meta.get("sector") and left_meta.get("sector") == right_meta.get("sector"):
        relation = "sector+correlation"
      links.append(
        {
          "source": left_symbol,
          "target": right_symbol,
          "value": round(abs(corr), 4),
          "direction": "positive" if corr >= 0 else "negative",
          "relation": relation,
        }
      )

  sector_groups = {}
  for item in members:
    sector = (item.get("sector") or "").strip()
    if not sector or item["symbol"] not in histories:
      continue
    sector_groups.setdefault(sector, []).append(item["symbol"])
  seen_pairs = {(min(link["source"], link["target"]), max(link["source"], link["target"])) for link in links}
  for sector_symbols in sector_groups.values():
    for index, left_symbol in enumerate(sector_symbols):
      for right_symbol in sector_symbols[index + 1 :]:
        pair = (min(left_symbol, right_symbol), max(left_symbol, right_symbol))
        if pair in seen_pairs:
          continue
        links.append(
          {
            "source": left_symbol,
            "target": right_symbol,
            "value": 0.35,
            "direction": "positive",
            "relation": "sector",
          }
        )
        seen_pairs.add(pair)

  output = {
    "universe": args.universe,
    "generatedAt": server.datetime.now(server.timezone.utc).isoformat(),
    "nodes": nodes,
    "links": sorted(links, key=lambda item: item["value"], reverse=True),
    "source": "Historical correlation + shared sector structure",
    "paperInspiredBy": [
      {
        "title": "Temporal Relational Ranking for Stock Prediction",
        "url": "https://arxiv.org/abs/1809.09441",
      },
      {
        "title": "HIST: A Graph-based Framework for Stock Trend Forecasting via Mining Concept-Oriented Shared Information",
        "url": "https://arxiv.org/abs/2110.13716",
      },
    ],
  }
  path = ROOT / "data" / "relations" / f"{args.universe}.json"
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(output, indent=2))
  print(json.dumps({"universe": args.universe, "nodes": len(nodes), "links": len(links), "path": str(path)}, indent=2))


if __name__ == "__main__":
  main()
