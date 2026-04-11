#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

import server


VAULT_DIR = ROOT / "vault" / "market-map"


def write_note(path: Path, content: str) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(content.strip() + "\n")


def slugify(value: str) -> str:
  return server.slugify_note_name(value)


def wiki(value: str) -> str:
  return f"[[{value}]]"


def load_members(universe_name: str) -> list[dict]:
  return server.load_universe_members(universe_name)


def load_relations(universe_name: str) -> dict:
  return server.load_relation_graph(universe_name)


def build_company_note(member: dict, related: list[dict], network: dict, note_summary: str) -> str:
  symbol = member.get("symbol", "")
  title = symbol
  name = member.get("name", symbol)
  sector = member.get("sector", "")
  region = member.get("region", "")
  exchange = member.get("exchange", "")
  relation_links = "\n".join(
    f"- {wiki(link['other'])} · `{link['direction']}` · strength {link['value']}"
    for link in related[:8]
  ) or "- No strong cached links yet."
  entity_links = "\n".join(
    f"- {entity.get('label')} · {entity.get('type', 'entity')}"
    for entity in network.get("entities", [])[:8]
  ) or "- No local entity map yet."
  return f"""
---
symbol: {symbol}
name: {name}
region: {region}
exchange: {exchange}
sector: {sector}
---

# {title}

{note_summary or f"{name} sits inside the local market graph as a {sector or 'market'} exposure for {region or 'global'} analysis."}

## Core context

- Name: {name}
- Exchange: {exchange}
- Region: {region}
- Sector: {sector}

## Graph neighbors

{relation_links}

## Entity map

{entity_links}

## Analyst note

- This note is generated from local universes, cached history, relation graphs, and repo KB notes.
- Use it as a durable context layer, not as a direct recommendation.
"""


def build_sector_note(sector: str, members: list[dict]) -> str:
  company_links = "\n".join(f"- {wiki(member['symbol'])}" for member in members[:20]) or "- No companies linked yet."
  return f"""
# {sector}

{sector} is maintained as a simple local concept node in the market-map vault.

## Companies

{company_links}
"""


def build_index_note(universe_stats: list[dict]) -> str:
  rows = "\n".join(
    f"- {item['label']} · {item['count']} members · relations file `{item['relationPath']}`"
    for item in universe_stats
  )
  return f"""
# Market Graph Index

This vault is the local markdown memory for the dashboard.

It is intentionally simple:

- universes are synced into JSON
- history is cached locally
- relations are generated from cached history
- notes are emitted as markdown with Obsidian-style wiki links

## Coverage

{rows}

## Key notes

- {wiki('Bond Regimes')}
- {wiki('Inflation Regimes')}
- {wiki('Factor Cadence and Significance')}
- {wiki('Market Graph Architecture')}
"""


def main() -> None:
  universe_map = [
    ("sensex30", "Sensex 30"),
    ("sp500", "S&P 500"),
    ("nasdaq_listed", "NASDAQ Listed"),
  ]
  company_networks = server.load_company_networks()
  universe_stats = []
  sector_groups: dict[str, list[dict]] = {}

  for universe_name, label in universe_map:
    members = load_members(universe_name)
    relations = load_relations(universe_name)
    relation_links = relations.get("links", [])
    relation_lookup: dict[str, list[dict]] = {}
    for link in relation_links:
      relation_lookup.setdefault(link["source"], []).append({"other": link["target"], "value": link.get("value"), "direction": link.get("direction", "neutral")})
      relation_lookup.setdefault(link["target"], []).append({"other": link["source"], "value": link.get("value"), "direction": link.get("direction", "neutral")})

    for member in members:
      sector = (member.get("sector") or "").strip()
      if sector:
        sector_groups.setdefault(sector, []).append(member)
      symbol = member.get("symbol", "")
      if not symbol:
        continue
      note = build_company_note(
        member,
        relation_lookup.get(symbol, []),
        company_networks.get(symbol, {}),
        server.company_note_for_symbol(symbol),
      )
      write_note(VAULT_DIR / "companies" / f"{symbol}.md", note)

    universe_stats.append(
      {
        "label": label,
        "count": len(members),
        "relationPath": f"data/relations/{universe_name}.json",
      }
    )

  for sector, members in sector_groups.items():
    write_note(VAULT_DIR / "sectors" / f"{slugify(sector)}.md", build_sector_note(sector, members))

  playbooks = {
    "Bond Regimes": ROOT / "kb" / "macro" / "bond-regimes.md",
    "Inflation Regimes": ROOT / "kb" / "macro" / "inflation-regimes.md",
    "Factor Cadence and Significance": ROOT / "kb" / "playbooks" / "factor-cadence-and-significance.md",
    "Market Graph Architecture": ROOT / "kb" / "playbooks" / "market-graph-architecture.md",
  }
  for title, source in playbooks.items():
    if source.exists():
      write_note(VAULT_DIR / "playbooks" / f"{title}.md", source.read_text())

  papers = server.load_trading_papers()
  for paper in papers:
    title = paper.get("title", "Paper")
    note = f"""
# {title}

- Year: {paper.get('year', '')}
- Type: {paper.get('type', '')}
- URL: {paper.get('url', '')}

## Factors

{chr(10).join(f"- {factor}" for factor in paper.get('factors', []))}

## Why it matters

{paper.get('whyItMatters', '')}
"""
    write_note(VAULT_DIR / "papers" / f"{slugify(title)}.md", note)

  write_note(VAULT_DIR / "Market Graph Index.md", build_index_note(universe_stats))
  print(json.dumps({"vault": str(VAULT_DIR), "universes": universe_stats, "papers": len(papers)}, indent=2))


if __name__ == "__main__":
  main()
