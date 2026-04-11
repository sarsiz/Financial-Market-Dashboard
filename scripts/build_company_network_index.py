#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

import server


OUTPUT_PATH = ROOT / "data" / "company_networks.generated.json"


def infer_macro_channel(symbol: str, sector: str, region: str) -> tuple[str, str]:
  symbol_upper = (symbol or "").upper()
  sector_lower = (sector or "").lower()
  if "bank" in sector_lower or symbol_upper.startswith("SBIN"):
    return "curve", "Rates and curve shape change net-interest sensitivity."
  if any(token in sector_lower for token in ["software", "technology", "semiconductor", "electronics"]):
    return "duration", "Long-duration growth names react strongly to real-yield repricing."
  if any(token in sector_lower for token in ["energy", "materials", "metals", "oil", "gas"]):
    return "commodity", "Commodity, inflation, and growth impulses dominate transmission."
  if any(token in sector_lower for token in ["pharma", "health", "biotech"]):
    return "regulation", "Policy, approvals, and pricing risk shape the path more than macro beta alone."
  if any(token in sector_lower for token in ["telecom", "communication"]):
    return "capex", "Capex cycle, pricing discipline, and subscriber demand dominate."
  return "growth", "Growth expectations and demand momentum are the main macro transmission channel."


def main() -> None:
  universe_map = [
    ("sensex30", "sensex30"),
    ("sp500", "sp500"),
    ("nasdaq_listed", "nasdaq_listed"),
  ]

  generated = {}
  for universe_name, universe_label in universe_map:
    members = server.load_universe_members(universe_name)
    relation_graph = server.load_relation_graph(universe_name)
    node_map = {item.get("symbol"): item for item in members if item.get("symbol")}
    neighbors = {}
    for link in relation_graph.get("links", []):
      source = link.get("source")
      target = link.get("target")
      if not source or not target:
        continue
      neighbors.setdefault(source, []).append({"symbol": target, "value": link.get("value", 0), "direction": link.get("direction", "neutral")})
      neighbors.setdefault(target, []).append({"symbol": source, "value": link.get("value", 0), "direction": link.get("direction", "neutral")})

    sector_groups = {}
    for member in members:
      sector = (member.get("sector") or "").strip()
      if sector:
        sector_groups.setdefault(sector, []).append(member.get("symbol"))

    for symbol, member in node_map.items():
      sector = member.get("sector", "")
      region = member.get("region", "")
      macro_channel, macro_note = infer_macro_channel(symbol, sector, region)
      peer_symbols = [peer for peer in sector_groups.get(sector, []) if peer and peer != symbol][:5]
      relation_entities = []
      for peer in peer_symbols:
        relation_entities.append(
          {
            "id": f"peer::{peer}",
            "label": node_map.get(peer, {}).get("name", peer),
            "type": "peer",
          }
        )
      relation_entities.extend(
        [
          {"id": f"sector::{server.slugify_note_name(sector or 'market')}", "label": sector or "Sector basket", "type": "sector"},
          {"id": f"macro::{macro_channel}", "label": macro_channel.title(), "type": "macro-channel"},
          {"id": f"universe::{universe_label}", "label": universe_label.upper(), "type": "universe"},
        ]
      )

      relation_links = []
      for peer in peer_symbols:
        peer_link = next((item for item in neighbors.get(symbol, []) if item["symbol"] == peer), None)
        relation_links.append(
          {
            "source": symbol,
            "target": f"peer::{peer}",
            "relation": "sector-peer",
            "direction": peer_link.get("direction", "positive") if peer_link else "positive",
            "value": float(peer_link.get("value", 0.6) if peer_link else 0.6),
          }
        )
      relation_links.extend(
        [
          {
            "source": f"sector::{server.slugify_note_name(sector or 'market')}",
            "target": symbol,
            "relation": "sector-membership",
            "direction": "neutral",
            "value": 0.8,
          },
          {
            "source": f"macro::{macro_channel}",
            "target": symbol,
            "relation": "macro-channel",
            "direction": "neutral",
            "value": 0.9,
          },
          {
            "source": f"universe::{universe_label}",
            "target": symbol,
            "relation": "index-membership",
            "direction": "neutral",
            "value": 0.7,
          },
        ]
      )

      generated[symbol] = {
        "entities": relation_entities,
        "links": relation_links,
        "profile": {
          "sector": sector,
          "region": region,
          "universe": universe_label,
          "macroChannel": macro_channel,
          "macroNote": macro_note,
          "peerCount": len(peer_symbols),
        },
      }

  OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
  OUTPUT_PATH.write_text(json.dumps(generated, indent=2))
  print(json.dumps({"path": str(OUTPUT_PATH), "companies": len(generated)}, indent=2))


if __name__ == "__main__":
  main()
