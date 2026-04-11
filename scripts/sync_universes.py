#!/usr/bin/env python3
from __future__ import annotations

import json
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


def main() -> None:
  sp500 = fetch_sp500_constituents()
  sensex = fetch_sensex_constituents()
  nasdaq = fetch_nasdaq_listed()

  write_json(DATA_DIR / "sp500.json", sp500)
  write_json(DATA_DIR / "sensex30.json", sensex)
  write_json(DATA_DIR / "nasdaq_listed.json", nasdaq)
  write_json(
    DATA_DIR / "manifest.json",
    {
      "generatedAt": server.datetime.now(server.timezone.utc).isoformat(),
      "universes": {
        "sp500": {"count": len(sp500), "path": "data/universes/sp500.json"},
        "sensex30": {"count": len(sensex), "path": "data/universes/sensex30.json"},
        "nasdaq_listed": {"count": len(nasdaq), "path": "data/universes/nasdaq_listed.json"},
      },
    },
  )
  print(json.dumps({"sp500": len(sp500), "sensex30": len(sensex), "nasdaq_listed": len(nasdaq)}, indent=2))


if __name__ == "__main__":
  main()
