#!/usr/bin/env python3
from __future__ import annotations

import json
import csv
import io
import re
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

import server


DATA_DIR = ROOT / "data" / "universes"


class TableParser(HTMLParser):
  def __init__(self):
    super().__init__()
    self.tables = []
    self._in_table = False
    self._in_row = False
    self._cell_tag = ""
    self._cell_text = []
    self._current_row = []
    self._current_table = []

  def handle_starttag(self, tag, attrs):
    if tag == "table":
      self._in_table = True
      self._current_table = []
    elif self._in_table and tag == "tr":
      self._in_row = True
      self._current_row = []
    elif self._in_row and tag in {"td", "th"}:
      self._cell_tag = tag
      self._cell_text = []

  def handle_endtag(self, tag):
    if self._in_row and tag == self._cell_tag and self._cell_tag:
      self._current_row.append(re.sub(r"\s+", " ", "".join(self._cell_text)).strip())
      self._cell_tag = ""
      self._cell_text = []
    elif self._in_row and tag == "tr":
      if any(cell for cell in self._current_row):
        self._current_table.append(self._current_row)
      self._current_row = []
      self._in_row = False
    elif self._in_table and tag == "table":
      if self._current_table:
        self.tables.append(self._current_table)
      self._current_table = []
      self._in_table = False

  def handle_data(self, data):
    if self._cell_tag:
      self._cell_text.append(data)


def write_json(path: Path, payload: dict | list) -> None:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(json.dumps(payload, indent=2, ensure_ascii=True))


def read_existing_universe(name: str) -> list[dict]:
  path = DATA_DIR / f"{name}.json"
  if not path.exists():
    return []
  try:
    payload = json.loads(path.read_text())
  except (json.JSONDecodeError, OSError):
    return []
  return payload if isinstance(payload, list) else []


def preserve_existing_if_empty(name: str, fetched: list[dict]) -> list[dict]:
  if fetched:
    return fetched
  existing = read_existing_universe(name)
  if existing:
    print(f"warning: keeping existing {name} universe because fetch returned 0 rows", file=sys.stderr)
  return existing


def normalize_yahoo_symbol(raw_symbol: str) -> str:
  symbol = (raw_symbol or "").strip().upper()
  if not symbol:
    return symbol
  return symbol.replace(".", "-")


def fetch_sp500_constituents() -> list[dict]:
  html_text = server.text_get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies") or ""
  parser = TableParser()
  parser.feed(html_text)
  for table in parser.tables:
    header = [cell.lower() for cell in table[0]]
    if "symbol" in header and "security" in header:
      rows = []
      for row in table[1:]:
        if len(row) < 4:
          continue
        rows.append(
          {
            "symbol": normalize_yahoo_symbol(row[0]),
            "rawSymbol": row[0].strip().upper(),
            "name": row[1].strip(),
            "sector": row[2].strip() if len(row) > 2 else "",
            "subIndustry": row[3].strip() if len(row) > 3 else "",
            "exchange": "S&P 500",
            "region": "us",
            "source": "Wikipedia S&P 500 companies",
          }
        )
      return rows
  return []


def fetch_sensex_constituents() -> list[dict]:
  html_text = server.text_get("https://en.wikipedia.org/wiki/List_of_BSE_SENSEX_companies") or ""
  parser = TableParser()
  parser.feed(html_text)
  for table in parser.tables:
    header = [cell.lower() for cell in table[0]]
    if "company" in header and "symbol" in header:
      rows = []
      for row in table[1:]:
        if len(row) < 4:
          continue
        raw_symbol = row[1].strip().upper()
        symbol = raw_symbol if raw_symbol.endswith(".BO") else f"{raw_symbol}.BO"
        rows.append(
          {
            "symbol": symbol,
            "rawSymbol": raw_symbol,
            "ticker": row[2].strip(),
            "name": row[0].strip(),
            "sector": row[3].strip(),
            "exchange": "BSE SENSEX",
            "region": "india",
            "source": "Wikipedia BSE SENSEX companies",
          }
        )
      return rows
  return []


def fetch_nasdaq_listed() -> list[dict]:
  text = server.text_get("https://nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt") or ""
  rows = []
  for line in text.splitlines():
    if not line or "|" not in line or line.startswith("Symbol|") or line.startswith("File Creation Time"):
      continue
    parts = line.split("|")
    if len(parts) < 2:
      continue
    symbol = parts[0].strip().upper()
    symbol = normalize_yahoo_symbol(symbol)
    name = parts[1].strip()
    if not symbol or not name:
      continue
    rows.append(
      {
        "symbol": symbol,
        "name": name,
        "exchange": "NASDAQ",
        "region": "us",
        "source": "NasdaqTrader Symbol Directory",
      }
    )
  return rows


def infer_nse_sector(symbol: str, name: str) -> str:
  fallback_sector = server.fallback_meta(symbol).get("sector")
  if fallback_sector and fallback_sector != "Other":
    return fallback_sector
  text = f"{symbol} {name}".lower()
  rules = [
    ("financials", ("bank", "finance", "financial", "finserv", "capital", "nbfc", "housing", "insurance", "securities", "microfinance", "asset management")),
    ("technology", ("tech", "software", "infotech", "systems", "digital", "data", "computer", "cyber", "solutions", "eclerx", "intellect")),
    ("healthcare", ("pharma", "pharmaceutical", "labs", "laboratories", "health", "hospital", "diagnostic", "life sciences", "biotech", "medic")),
    ("consumer discretionary", ("auto", "motors", "suzuki", "vehicle", "tyre", "jewellery", "retail", "fashion", "hotel", "travel", "leisure", "entertainment")),
    ("consumer staples", ("foods", "food", "beverage", "brewer", "consumer", "unilever", "fmcg", "agro", "tea", "sugar", "dairy", "tobacco")),
    ("industrials", ("engineering", "infra", "infrastructure", "construction", "logistics", "transport", "shipping", "ports", "aerospace", "defence", "industrial")),
    ("materials", ("steel", "metal", "mining", "cement", "chem", "paint", "glass", "paper", "textile", "plast", "poly", "fertilis", "ceramic", "aluminium", "copper")),
    ("energy", ("oil", "gas", "petro", "energy", "coal", "refinery", "lng")),
    ("utilities", ("power", "grid", "electric", "utilities", "renewable", "solar", "wind")),
    ("communication services", ("telecom", "communication", "media", "broadcast", "network")),
    ("real estate", ("realty", "estate", "developer", "properties", "housing development")),
  ]
  for sector, keywords in rules:
    if any(keyword in text for keyword in keywords):
      return sector
  return "Other"


def fetch_nse_all_equities() -> list[dict]:
  urls = [
    "https://archives.nseindia.com/content/equities/EQUITY_L.csv",
    "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv",
  ]
  text = ""
  source_url = ""
  for url in urls:
    text = server.text_get(url) or ""
    if "SYMBOL" in text.upper() and "," in text:
      source_url = url
      break
  if not text:
    return []

  rows = []
  reader = csv.DictReader(io.StringIO(text))
  for rank, row in enumerate(reader, start=1):
    raw_symbol = (row.get("SYMBOL") or "").strip().upper()
    name = (row.get("NAME OF COMPANY") or row.get("NAME") or raw_symbol).strip()
    series = (row.get("SERIES") or "").strip().upper()
    isin = (row.get("ISIN NUMBER") or row.get("ISIN") or "").strip().upper()
    if not raw_symbol or not name:
      continue
    symbol = raw_symbol if raw_symbol.endswith(".NS") else f"{raw_symbol}.NS"
    rows.append(
      {
        "symbol": symbol,
        "rawSymbol": raw_symbol,
        "name": name,
        "series": series,
        "isin": isin,
        "sector": infer_nse_sector(symbol, name),
        "exchange": "NSE",
        "region": "india",
        "rank": rank,
        "source": f"NSE equity securities list ({source_url or 'EQUITY_L.csv'})",
      }
    )
  return rows


def main() -> None:
  sp500 = preserve_existing_if_empty("sp500", fetch_sp500_constituents())
  sensex = preserve_existing_if_empty("sensex30", fetch_sensex_constituents())
  nse_all = preserve_existing_if_empty("nse_all", fetch_nse_all_equities())
  nasdaq = preserve_existing_if_empty("nasdaq_listed", fetch_nasdaq_listed())

  write_json(DATA_DIR / "sp500.json", sp500)
  write_json(DATA_DIR / "sensex30.json", sensex)
  write_json(DATA_DIR / "nse_all.json", nse_all)
  write_json(DATA_DIR / "nasdaq_listed.json", nasdaq)
  write_json(
    DATA_DIR / "manifest.json",
    {
      "generatedAt": server.datetime.now(server.timezone.utc).isoformat(),
      "universes": {
        "sp500": {"count": len(sp500), "path": "data/universes/sp500.json"},
        "sensex30": {"count": len(sensex), "path": "data/universes/sensex30.json"},
        "nse_all": {"count": len(nse_all), "path": "data/universes/nse_all.json"},
        "nasdaq_listed": {"count": len(nasdaq), "path": "data/universes/nasdaq_listed.json"},
      },
    },
  )
  print(json.dumps({"sp500": len(sp500), "sensex30": len(sensex), "nse_all": len(nse_all), "nasdaq_listed": len(nasdaq)}, indent=2))


if __name__ == "__main__":
  main()
