#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

import server

JOB_DIR = ROOT / "data" / "jobs"


def load_universe(name: str) -> list[dict]:
  path = ROOT / "data" / "universes" / f"{name}.json"
  if not path.exists():
    raise SystemExit(f"Universe file not found: {path}")
  return json.loads(path.read_text())


def backfill_one(symbol: str, chart_range: str) -> dict:
  history, meta = server.build_history(symbol, chart_range)
  return {
    "symbol": symbol,
    "points": len(history),
    "source": meta.get("historySource", "Unavailable"),
    "cacheState": meta.get("historyCacheState", "miss"),
  }


def write_job_state(path: Path, payload: dict) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(payload, indent=2))


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--universe", required=True, help="sensex30 | sp500 | nasdaq_listed")
  parser.add_argument("--range", default="1Y")
  parser.add_argument("--limit", type=int, default=0)
  parser.add_argument("--offset", type=int, default=0)
  parser.add_argument("--workers", type=int, default=8)
  parser.add_argument("--job-name", default="")
  args = parser.parse_args()

  members = load_universe(args.universe)
  if args.offset > 0:
    members = members[args.offset :]
  if args.limit > 0:
    members = members[: args.limit]
  symbols = [item["symbol"] for item in members if item.get("symbol")]
  job_name = args.job_name or f"{args.universe.lower()}_{args.range.lower()}_{args.offset}_{len(symbols)}"
  job_path = JOB_DIR / f"{job_name}.json"

  results = []
  write_job_state(
    job_path,
    {
      "jobName": job_name,
      "universe": args.universe,
      "range": args.range,
      "offset": args.offset,
      "members": len(symbols),
      "completed": 0,
      "startedAt": server.datetime.now(server.timezone.utc).isoformat(),
      "results": [],
    },
  )
  with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
    futures = {executor.submit(backfill_one, symbol, args.range): symbol for symbol in symbols}
    for future in as_completed(futures):
      symbol = futures[future]
      try:
        results.append(future.result())
      except Exception as error:
        results.append({"symbol": symbol, "points": 0, "source": f"ERROR: {error}", "cacheState": "miss"})
      write_job_state(
        job_path,
        {
          "jobName": job_name,
          "universe": args.universe,
          "range": args.range,
          "offset": args.offset,
          "members": len(symbols),
          "completed": len(results),
          "updatedAt": server.datetime.now(server.timezone.utc).isoformat(),
          "results": results[-100:],
        },
      )

  print(
    json.dumps(
      {
        "jobName": job_name,
        "universe": args.universe,
        "range": args.range,
        "members": len(symbols),
        "withHistory": sum(1 for item in results if item["points"] >= 2),
        "jobPath": str(job_path),
        "results": results[:20],
      },
      indent=2,
    )
  )


if __name__ == "__main__":
  main()
