#!/usr/bin/env python3
"""Fail when a Git tree contains private market data or likely credentials."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZERO_SHA = "0" * 40
MAX_TEXT_BYTES = 2_000_000

FORBIDDEN_EXACT_PATHS = {
  ".env",
  "config.json",
  "financial_board.db",
  "financial_board.db-shm",
  "financial_board.db-wal",
  "strategy_config.json",
  "signal_override.json",
}

FORBIDDEN_SUFFIXES = {
  ".db",
  ".key",
  ".pem",
  ".private.json",
  ".secret.json",
  ".session.json",
  ".sqlite",
  ".sqlite3",
}

HIGH_CONFIDENCE_PATTERNS = (
  ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
  ("OpenAI-style key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
  ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
  ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
  ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
  ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
)

KITE_ASSIGNMENT_PATTERN = re.compile(
  r"""(?ix)
  \b(
    kite[_-]?(?:api[_-]?secret|access[_-]?token|request[_-]?token)
    |api[_-]?secret
    |access[_-]?token
    |request[_-]?token
    |enctoken
  )\b
  \s*[:=]\s*
  ["']([^"']{8,})["']
  """
)

PLACEHOLDER_MARKERS = (
  "changeme",
  "dummy",
  "example",
  "placeholder",
  "request_token_here",
  "test",
  "your_",
  "xxx",
  "yyy",
  "zzz",
)


def run_git(*args: str, check: bool = True) -> bytes:
  return subprocess.run(
    ["git", *args],
    cwd=ROOT,
    check=check,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
  ).stdout


def is_forbidden_path(path: str) -> bool:
  normalized = path.replace("\\", "/")
  while normalized.startswith("./"):
    normalized = normalized[2:]
  lowered = normalized.lower()
  name = Path(lowered).name

  if lowered in FORBIDDEN_EXACT_PATHS:
    return True
  if lowered.startswith("vault/") or lowered.startswith(".kite/"):
    return True
  if lowered.startswith(("data/", "kb/")) and name != ".gitkeep":
    return True
  if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
    return True
  if any(name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES):
    return True
  if name.startswith(("kite_", "zerodha_")) and name.endswith((".json", ".env", ".csv")):
    return True
  if name.startswith(("broker_session", "auth_callback")) and name.endswith(".json"):
    return True
  return False


def is_placeholder(value: str) -> bool:
  lowered = value.strip().lower()
  return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def scan_text(path: str, raw: bytes) -> list[str]:
  if len(raw) > MAX_TEXT_BYTES or b"\0" in raw:
    return []
  text = raw.decode("utf-8", errors="ignore")
  findings: list[str] = []

  for label, pattern in HIGH_CONFIDENCE_PATTERNS:
    if pattern.search(text):
      findings.append(f"{path}: contains a likely {label}")

  for match in KITE_ASSIGNMENT_PATTERN.finditer(text):
    value = match.group(2)
    if not is_placeholder(value):
      line = text.count("\n", 0, match.start()) + 1
      findings.append(f"{path}:{line}: contains a literal broker credential")
  return findings


def tracked_paths() -> list[str]:
  return [
    item.decode("utf-8")
    for item in run_git("ls-files", "-z").split(b"\0")
    if item
  ]


def revision_paths(revision: str) -> list[str]:
  return [
    item.decode("utf-8")
    for item in run_git("ls-tree", "-r", "--name-only", "-z", revision).split(b"\0")
    if item
  ]


def scan_worktree() -> list[str]:
  findings: list[str] = []
  for path in tracked_paths():
    if is_forbidden_path(path):
      findings.append(f"{path}: private path must not be tracked")
      continue
    candidate = ROOT / path
    if candidate.is_file():
      findings.extend(scan_text(path, candidate.read_bytes()))
  return findings


def new_revisions(local_sha: str, remote_sha: str) -> list[str]:
  if remote_sha and remote_sha != ZERO_SHA:
    result = run_git("rev-list", f"{remote_sha}..{local_sha}", check=False)
  else:
    result = run_git("rev-list", local_sha, "--not", "--remotes=origin", check=False)
    if not result.strip():
      result = run_git("rev-list", "-1", local_sha)
  return [line for line in result.decode("ascii", errors="ignore").splitlines() if line]


def scan_revisions(local_sha: str, remote_sha: str) -> list[str]:
  findings: set[str] = set()
  for revision in new_revisions(local_sha, remote_sha):
    for path in revision_paths(revision):
      if is_forbidden_path(path):
        findings.add(f"{revision[:12]} {path}: private path is present in pushed history")
        continue
      raw = run_git("show", f"{revision}:{path}", check=False)
      for finding in scan_text(path, raw):
        findings.add(f"{revision[:12]} {finding}")
  return sorted(findings)


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--local", help="Local commit SHA being pushed")
  parser.add_argument("--remote", default=ZERO_SHA, help="Remote commit SHA before the push")
  args = parser.parse_args()

  findings = scan_revisions(args.local, args.remote) if args.local else scan_worktree()
  if findings:
    print("Repository safety check failed:", file=sys.stderr)
    for finding in findings:
      print(f"- {finding}", file=sys.stderr)
    print("Remove the private material and rotate any exposed credential before pushing.", file=sys.stderr)
    return 1

  print("Repository safety check passed.")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
