#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"


def run_step(args: list[str]) -> str:
  completed = subprocess.run(
    [sys.executable, *args],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
  )
  return completed.stdout.strip()


def main() -> None:
  parser = argparse.ArgumentParser()
  parser.add_argument("--nasdaq-limit", type=int, default=250)
  parser.add_argument("--workers", type=int, default=10)
  args = parser.parse_args()

  outputs = {
    "universes": json.loads(run_step([str(SCRIPTS_DIR / "sync_universes.py")])),
    "backfills": {},
    "relations": {},
  }

  backfill_jobs = [
    ("sensex30", 0),
    ("sp500", 0),
    ("nasdaq_listed", args.nasdaq_limit),
  ]
  for universe_name, limit in backfill_jobs:
    command = [
      str(SCRIPTS_DIR / "backfill_history.py"),
      "--universe",
      universe_name,
      "--range",
      "1Y",
      "--workers",
      str(args.workers),
    ]
    if limit > 0:
      command.extend(["--limit", str(limit)])
    outputs["backfills"][universe_name] = json.loads(run_step(command))
    outputs["relations"][universe_name] = json.loads(
      run_step(
        [
          str(SCRIPTS_DIR / "build_relations.py"),
          "--universe",
          universe_name,
          *(["--limit", str(limit)] if limit > 0 else []),
        ]
      )
    )

  outputs["companyNetworks"] = json.loads(run_step([str(SCRIPTS_DIR / "build_company_network_index.py")]))
  outputs["vault"] = json.loads(run_step([str(SCRIPTS_DIR / "build_market_map_vault.py")]))

  print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
  main()
