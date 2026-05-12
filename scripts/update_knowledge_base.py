#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

DEFAULT_BUILD_STEPS = [
  "build_research_protocol_vault.py",
  "build_agent_memory_vault.py",
]

FULL_MARKET_MAP_STEP = "build_market_map_vault.py"

BLOCKED_TERMS = [
  "Obs" + "idian",
  "obs" + "idian",
  "Kar" + "pathy",
  "kar" + "pathy",
]


def run_step(script_name: str) -> dict:
  script_path = SCRIPTS / script_name
  result = subprocess.run(
    [sys.executable, str(script_path)],
    cwd=ROOT,
    check=True,
    capture_output=True,
    text=True,
  )
  output = result.stdout.strip()
  if not output:
    return {"script": script_name, "status": "ok"}
  try:
    payload = json.loads(output)
  except json.JSONDecodeError:
    payload = {"output": output}
  return {"script": script_name, "status": "ok", "result": payload}


def markdown_files() -> list[Path]:
  roots = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "CLAUDE.md", ROOT / "kb", ROOT / "vault" / "market-map"]
  files: list[Path] = []
  for root in roots:
    if root.is_file() and root.suffix == ".md":
      files.append(root)
    elif root.exists():
      files.extend(path for path in root.rglob("*.md") if path.is_file())
  return sorted(files)


def find_blocked_terms() -> list[dict]:
  matches = []
  for path in markdown_files():
    text = path.read_text(errors="ignore")
    for line_no, line in enumerate(text.splitlines(), start=1):
      if any(term in line for term in BLOCKED_TERMS):
        matches.append(
          {
            "path": str(path.relative_to(ROOT)),
            "line": line_no,
            "text": line.strip(),
          }
        )
  return matches


def parse_args() -> ArgumentParser:
  parser = ArgumentParser(description="Refresh generated markdown notes and validate project docs.")
  parser.add_argument(
    "--full-market-map",
    action="store_true",
    help="Also rebuild generated company and sector market-map notes.",
  )
  return parser


def main() -> None:
  args = parse_args().parse_args()
  steps = ([FULL_MARKET_MAP_STEP] if args.full_market_map else []) + DEFAULT_BUILD_STEPS
  results = [run_step(script_name) for script_name in steps]
  blocked = find_blocked_terms()
  payload = {
    "status": "blocked_terms_found" if blocked else "ok",
    "steps": results,
    "checkedMarkdownFiles": len(markdown_files()),
    "blockedTerms": blocked,
  }
  print(json.dumps(payload, indent=2))
  if blocked:
    raise SystemExit(1)


if __name__ == "__main__":
  main()
