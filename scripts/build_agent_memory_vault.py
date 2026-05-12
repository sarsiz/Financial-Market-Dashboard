#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VAULT_DIR = ROOT / "vault" / "market-map"
META_DIR = VAULT_DIR / "_meta"
INBOX_DIR = VAULT_DIR / "inbox"
SESSIONS_DIR = VAULT_DIR / "sessions"
SOURCES_DIR = VAULT_DIR / "sources"
TEMPLATES_DIR = VAULT_DIR / "templates"


def ensure_dirs() -> None:
  for path in [META_DIR, INBOX_DIR, SESSIONS_DIR, SOURCES_DIR, TEMPLATES_DIR]:
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str) -> None:
  path.write_text(content.strip() + "\n")


def count_notes(folder: Path) -> int:
  if not folder.exists():
    return 0
  return sum(1 for path in folder.rglob("*.md") if path.is_file())


def build_manifest() -> dict:
  return {
    "companies": count_notes(VAULT_DIR / "companies"),
    "concepts": count_notes(VAULT_DIR / "concepts"),
    "papers": count_notes(VAULT_DIR / "papers"),
    "playbooks": count_notes(VAULT_DIR / "playbooks"),
    "research": count_notes(VAULT_DIR / "research"),
    "sectors": count_notes(VAULT_DIR / "sectors"),
    "workflows": count_notes(VAULT_DIR / "workflows"),
  }


def write_manifest_notes(manifest: dict) -> None:
  write(
    META_DIR / "Vault Manifest.md",
    f"""
# Vault Manifest

This is the local knowledge base for the financial dashboard.

## Coverage

- Companies: {manifest['companies']}
- Concepts: {manifest['concepts']}
- Papers: {manifest['papers']}
- Playbooks: {manifest['playbooks']}
- Research notes: {manifest['research']}
- Sectors: {manifest['sectors']}
- Workflows: {manifest['workflows']}

## Memory rules

- Keep generated knowledge deterministic and scriptable.
- Prefer one note per durable concept, company, sector, paper, or workflow.
- Use inbox notes for raw captures before promoting them into durable notes.
- Use session notes for current investigation threads, not for permanent facts.
- Link durable notes with simple `[[note]]` links where useful.
""",
  )
  write(
    META_DIR / "Agent Memory Protocol.md",
    """
# Agent Memory Protocol

This vault follows a simple local-first memory pattern:

## Durable memory

- `companies/`: one note per company or ticker
- `concepts/`: factor or quant concept notes
- `papers/`: paper summaries and dashboard use
- `playbooks/`: interpretation guides
- `research/`: factor registry notes
- `sectors/`: sector concept nodes
- `workflows/`: factor-flow and decision-flow notes

## Working memory

- `sessions/`: current research sessions and temporary synthesis
- `inbox/`: raw captures waiting to be promoted
- `sources/`: source landing notes and provenance summaries

## Promotion rule

If a note is still tied to a single run or debugging session, keep it in `sessions/` or `inbox/`.
If it is reusable across future work, promote it to a durable folder.

## Why this exists

This keeps the repo easy to inspect and maintain:
- plain markdown
- easy diffs
- easy grep
- generated indexes
- no hidden database required for core understanding
""",
  )


def write_working_memory_notes() -> None:
  write(
    INBOX_DIR / "README.md",
    """
# Inbox

Drop raw market observations, article summaries, or one-off captures here before promoting them into durable notes.

Promotion targets:
- company-specific facts -> `companies/`
- reusable factor logic -> `concepts/`
- repeatable interpretation rules -> `playbooks/`
- paper-backed methodology -> `papers/` or `research/`
""",
  )
  write(
    SESSIONS_DIR / "Current Focus.md",
    """
# Current Focus

Use this note for temporary synthesis during a live implementation or market investigation.

Suggested sections:
- What changed
- Why it matters
- Unknowns
- Promote to durable notes
""",
  )
  write(
    SOURCES_DIR / "Source Capture Guide.md",
    """
# Source Capture Guide

When saving source-backed facts, keep:
- source title
- URL
- timestamp or publication date
- what fact was extracted
- where it should be used in the dashboard

Do not mix raw source capture with durable interpretation without making that distinction explicit.
""",
  )
  write(
    TEMPLATES_DIR / "Durable Note Template.md",
    """
---
title:
type:
source:
updated:
---

# Title

## Fact

## Interpretation

## Dashboard use

## Related notes
""",
  )


def main() -> None:
  ensure_dirs()
  manifest = build_manifest()
  write_manifest_notes(manifest)
  write_working_memory_notes()
  (META_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
  print(json.dumps({"vault": str(VAULT_DIR), "meta": str(META_DIR), "manifest": manifest}, indent=2))


if __name__ == "__main__":
  main()
