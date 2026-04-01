from __future__ import annotations

import json
import html
import math
import re
import sqlite3
import statistics
import time
import threading
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "financial_board.db"
CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_CONFIG = {
  "provider": "yahoo",
  "alphaVantageApiKey": "",
  "localLlmBaseUrl": "http://127.0.0.1:11434",
  "localLlmModel": "Bonsai-8B-1bit",
}

DEFAULT_WATCHLIST = ["BHARTIARTL.NS", "ICICIBANK.NS", "GLENMARK.NS"]

FALLBACK_TICKERS = {
  "AAPL": {"name": "Apple", "basePrice": 212.4, "currency": "USD", "exchange": "NASDAQ", "beta": 1.08, "pe": 31.4},
  "MSFT": {"name": "Microsoft", "basePrice": 428.8, "currency": "USD", "exchange": "NASDAQ", "beta": 0.92, "pe": 36.2},
  "NVDA": {"name": "NVIDIA", "basePrice": 928.1, "currency": "USD", "exchange": "NASDAQ", "beta": 1.74, "pe": 63.1},
  "AMZN": {"name": "Amazon", "basePrice": 183.1, "currency": "USD", "exchange": "NASDAQ", "beta": 1.18, "pe": 44.5},
  "META": {"name": "Meta Platforms", "basePrice": 498.7, "currency": "USD", "exchange": "NASDAQ", "beta": 1.22, "pe": 27.4},
  "GOOGL": {"name": "Alphabet", "basePrice": 161.5, "currency": "USD", "exchange": "NASDAQ", "beta": 1.04, "pe": 25.7},
  "TSLA": {"name": "Tesla", "basePrice": 184.2, "currency": "USD", "exchange": "NASDAQ", "beta": 2.03, "pe": 58.9},
  "AMD": {"name": "AMD", "basePrice": 178.9, "currency": "USD", "exchange": "NASDAQ", "beta": 1.62, "pe": 49.8},
  "RELIANCE.NS": {"name": "Reliance Industries", "basePrice": 2940.0, "currency": "INR", "exchange": "NSE", "beta": 0.96, "pe": 28.3},
  "BHARTIARTL.NS": {"name": "Bharti Airtel", "basePrice": 1228.0, "currency": "INR", "exchange": "NSE", "beta": 0.84, "pe": 54.0},
  "ICICIBANK.NS": {"name": "ICICI Bank", "basePrice": 1094.0, "currency": "INR", "exchange": "NSE", "beta": 0.89, "pe": 18.8},
  "GLENMARK.NS": {"name": "Glenmark Pharma", "basePrice": 1168.0, "currency": "INR", "exchange": "NSE", "beta": 0.93, "pe": 21.7},
  "TCS.NS": {"name": "TCS", "basePrice": 4125.0, "currency": "INR", "exchange": "NSE", "beta": 0.81, "pe": 31.2},
  "INFY.NS": {"name": "Infosys", "basePrice": 1518.0, "currency": "INR", "exchange": "NSE", "beta": 0.88, "pe": 24.6},
  "HDFCBANK.NS": {"name": "HDFC Bank", "basePrice": 1528.0, "currency": "INR", "exchange": "NSE", "beta": 0.77, "pe": 19.4},
}

MARKET_SUFFIXES = {
  "us": "",
  "nasdaq": "",
  "sp500": "",
  "nse": ".NS",
  "bse": ".BO",
  "asx": ".AX",
  "lse": ".L",
  "jpx": ".T",
  "xetra": ".DE",
}

MACRO_SYMBOLS = [
  {"label": "S&P 500", "symbol": "^GSPC"},
  {"label": "NASDAQ 100", "symbol": "^NDX"},
  {"label": "NIFTY 50", "symbol": "^NSEI"},
  {"label": "US 10Y Yield", "symbol": "^TNX"},
  {"label": "WTI Crude", "symbol": "CL=F"},
  {"label": "Gold", "symbol": "GC=F"},
]

MARKET_PRESETS = [
  {
    "name": "nasdaq_core",
    "label": "NASDAQ Core",
    "symbols": ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AMD"],
  },
  {
    "name": "sp500_leaders",
    "label": "S&P 500 Leaders",
    "symbols": ["AAPL", "MSFT", "NVDA", "JPM", "XOM", "LLY", "BRK-B", "V"],
  },
  {
    "name": "nse_leaders",
    "label": "NSE Leaders",
    "symbols": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "LT.NS", "ITC.NS"],
  },
  {
    "name": "global_macro",
    "label": "Global Macro",
    "symbols": ["^GSPC", "^IXIC", "^NSEI", "CL=F", "GC=F", "DX-Y.NYB"],
  },
]

RESEARCH_REFERENCES = [
  {
    "title": "Chronos: Learning the Language of Time Series",
    "year": 2024,
    "url": "https://arxiv.org/abs/2403.07815",
  },
  {
    "title": "TimesFM",
    "year": 2024,
    "url": "https://arxiv.org/abs/2310.10688",
  },
  {
    "title": "A Time Series is Worth 64 Words",
    "year": 2023,
    "url": "https://arxiv.org/abs/2211.14730",
  },
  {
    "title": "Moirai 2.0",
    "year": 2025,
    "url": "https://arxiv.org/abs/2511.11698",
  },
]

FALLBACK_HEADLINES = [
  "Rates repricing is spilling into equity leadership and compressing long-duration valuations.",
  "AI infrastructure names remain crowded as earnings revisions separate real beneficiaries from thematic passengers.",
  "Energy and shipping sensitivity is back in focus as growth and inflation signals diverge across regions.",
  "Currency volatility is lifting event risk for exporters and globally diversified earnings baskets.",
  "Crowded winners face higher reaction risk when macro data collides with elevated expectations.",
]

FALLBACK_MACRO_PULSE = [
  {"label": "S&P 500", "value": "5148.22", "trend": "+0.34%", "positive": True},
  {"label": "NASDAQ 100", "value": "18042.11", "trend": "+0.58%", "positive": True},
  {"label": "NIFTY 50", "value": "22431.65", "trend": "-0.21%", "positive": False},
  {"label": "US 10Y Yield", "value": "4.19%", "trend": "+0.08%", "positive": False},
  {"label": "WTI Crude", "value": "82.40 USD", "trend": "+1.12%", "positive": False},
  {"label": "Gold", "value": "2238.10 USD", "trend": "+0.46%", "positive": True},
]

EVENT_CATEGORY_QUERIES = {
  "business": "latest global business news markets earnings deals",
  "world": "latest world news geopolitics economy today",
  "war": "latest war news global conflict defense markets today",
  "layoffs": "latest layoffs news companies technology finance today",
  "partnerships": "latest company partnerships business strategic alliance today",
  "deals": "latest mergers acquisitions deals companies today",
  "brands": "latest brand launches campaigns retail consumer brands today",
}

RADAR_REGION_KEYWORDS = {
  "north_america": {"us", "usa", "united states", "canada", "washington", "new york", "california", "mexico"},
  "south_america": {"brazil", "argentina", "chile", "colombia", "peru", "venezuela"},
  "europe": {"europe", "eu", "uk", "britain", "germany", "france", "italy", "spain", "nato", "brussels", "london", "ukraine", "russia"},
  "africa": {"africa", "egypt", "south africa", "nigeria", "ethiopia", "sudan"},
  "middle_east": {"iran", "israel", "gaza", "saudi", "uae", "qatar", "yemen", "lebanon", "syria", "iraq", "middle east"},
  "south_asia": {"india", "pakistan", "bangladesh", "sri lanka", "nse", "mumbai", "delhi"},
  "east_asia": {"china", "taiwan", "japan", "korea", "south korea", "north korea", "hong kong", "beijing", "tokyo"},
}

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36"
DB_LOCK = threading.Lock()


def load_config() -> dict:
  if CONFIG_PATH.exists():
    try:
      return {**DEFAULT_CONFIG, **json.loads(CONFIG_PATH.read_text())}
    except json.JSONDecodeError:
      return DEFAULT_CONFIG.copy()
  return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> dict:
  payload = {
    "provider": config.get("provider", "yahoo"),
    "alphaVantageApiKey": config.get("alphaVantageApiKey", "").strip(),
    "localLlmBaseUrl": config.get("localLlmBaseUrl", DEFAULT_CONFIG["localLlmBaseUrl"]).strip() or DEFAULT_CONFIG["localLlmBaseUrl"],
    "localLlmModel": config.get("localLlmModel", DEFAULT_CONFIG["localLlmModel"]).strip() or DEFAULT_CONFIG["localLlmModel"],
  }
  CONFIG_PATH.write_text(json.dumps(payload, indent=2))
  return payload


def init_db() -> None:
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      connection.execute(
        """
        CREATE TABLE IF NOT EXISTS watchlists (
          name TEXT PRIMARY KEY,
          symbols_json TEXT NOT NULL,
          updated_at TEXT NOT NULL
        )
        """
      )
      connection.execute(
        """
        CREATE TABLE IF NOT EXISTS history_cache (
          symbol TEXT NOT NULL,
          chart_range TEXT NOT NULL,
          closes_json TEXT NOT NULL,
          meta_json TEXT NOT NULL,
          source TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          PRIMARY KEY(symbol, chart_range)
        )
        """
      )
      connection.commit()
    finally:
      connection.close()


def save_watchlist(name: str, symbols: list[str]) -> None:
  payload = json.dumps(symbols)
  updated_at = datetime.now(timezone.utc).isoformat()
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      connection.execute(
        """
        INSERT INTO watchlists(name, symbols_json, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
          symbols_json = excluded.symbols_json,
          updated_at = excluded.updated_at
        """,
        (name, payload, updated_at),
      )
      connection.commit()
    finally:
      connection.close()


def list_watchlists() -> list[dict]:
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      rows = connection.execute(
        "SELECT name, symbols_json, updated_at FROM watchlists ORDER BY updated_at DESC"
      ).fetchall()
    finally:
      connection.close()

  items = []
  for name, symbols_json, updated_at in rows:
    symbols = json.loads(symbols_json)
    items.append(
      {
        "name": name,
        "symbols": symbols,
        "count": len(symbols),
        "updatedAt": updated_at,
      }
    )
  return items


HISTORY_CACHE_MAX_AGE = {
  "1D": 90,
  "3D": 300,
  "5D": 600,
  "1M": 3600,
  "1Y": 21600,
}


def history_cache_ttl(chart_range: str) -> int:
  return HISTORY_CACHE_MAX_AGE.get((chart_range or "1M").upper(), HISTORY_CACHE_MAX_AGE["1M"])


def load_cached_history(symbol: str, chart_range: str) -> tuple[list[float], dict, str, str] | None:
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      row = connection.execute(
        """
        SELECT closes_json, meta_json, source, updated_at
        FROM history_cache
        WHERE symbol = ? AND chart_range = ?
        """,
        (symbol.upper(), chart_range.upper()),
      ).fetchone()
    finally:
      connection.close()
  if not row:
    return None
  closes_json, meta_json, source, updated_at = row
  try:
    closes = [float(value) for value in json.loads(closes_json)]
    meta = json.loads(meta_json)
  except (TypeError, ValueError, json.JSONDecodeError):
    return None
  return closes, meta if isinstance(meta, dict) else {}, source, updated_at


def save_history_cache(symbol: str, chart_range: str, closes: list[float], meta: dict, source: str) -> None:
  payload = json.dumps([round(float(value), 6) for value in closes])
  meta_payload = json.dumps(meta or {})
  updated_at = datetime.now(timezone.utc).isoformat()
  with DB_LOCK:
    connection = sqlite3.connect(DB_PATH)
    try:
      connection.execute(
        """
        INSERT INTO history_cache(symbol, chart_range, closes_json, meta_json, source, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(symbol, chart_range) DO UPDATE SET
          closes_json = excluded.closes_json,
          meta_json = excluded.meta_json,
          source = excluded.source,
          updated_at = excluded.updated_at
        """,
        (symbol.upper(), chart_range.upper(), payload, meta_payload, source, updated_at),
      )
      connection.commit()
    finally:
      connection.close()


def build_cached_meta(meta: dict, source: str, updated_at: str, stale: bool = False) -> dict:
  payload = dict(meta or {})
  payload["historySource"] = source
  payload["historyCachedAt"] = updated_at
  payload["historyCacheState"] = "stale" if stale else "fresh"
  return payload


def json_get(url: str) -> dict | list | None:
  candidates = [url]
  if "query1.finance.yahoo.com" in url:
    candidates.append(url.replace("query1.finance.yahoo.com", "query2.finance.yahoo.com"))
  elif "query2.finance.yahoo.com" in url:
    candidates.append(url.replace("query2.finance.yahoo.com", "query1.finance.yahoo.com"))

  header_sets = [
    {"User-Agent": USER_AGENT},
    {"User-Agent": USER_AGENT, "Referer": "https://finance.yahoo.com/"},
  ]

  for candidate in dict.fromkeys(candidates):
    for headers in header_sets:
      request = urllib.request.Request(candidate, headers=headers)
      try:
        with urllib.request.urlopen(request, timeout=16) as response:
          return json.loads(response.read().decode("utf-8"))
      except urllib.error.HTTPError as error:
        if error.code not in {403, 429}:
          continue
        time.sleep(0.2)
      except Exception:
        continue
  return None


def text_get(url: str) -> str | None:
  request = urllib.request.Request(
    url,
    headers={
      "User-Agent": USER_AGENT,
      "Accept": "application/rss+xml,application/xml,text/xml,text/plain,*/*",
    },
  )
  try:
    with urllib.request.urlopen(request, timeout=12) as response:
      return response.read().decode("utf-8", errors="replace")
  except Exception:
    return None


def visible_text_lines(html_text: str) -> list[str]:
  cleaned = re.sub(r"<script\b[^>]*>.*?</script>", " ", html_text, flags=re.IGNORECASE | re.DOTALL)
  cleaned = re.sub(r"<style\b[^>]*>.*?</style>", " ", cleaned, flags=re.IGNORECASE | re.DOTALL)
  cleaned = re.sub(r"<[^>]+>", "\n", cleaned)
  cleaned = html.unescape(cleaned)
  lines = []
  for raw in cleaned.splitlines():
    text = re.sub(r"\s+", " ", raw).strip()
    if text:
      lines.append(text)
  return lines


def parse_number(text: str) -> float | None:
  cleaned = re.sub(r"[^\d.\-]", "", text or "")
  if not cleaned or cleaned in {"-", ".", "-."}:
    return None
  try:
    return float(cleaned)
  except ValueError:
    return None


def parse_compact_number(text: str) -> float | None:
  match = re.search(r"(-?[\d,.]+)\s*([KMBT])?", text or "", re.IGNORECASE)
  if not match:
    return None
  number = parse_number(match.group(1))
  if number is None:
    return None
  multiplier = {"K": 1e3, "M": 1e6, "B": 1e9, "T": 1e12}.get((match.group(2) or "").upper(), 1)
  return number * multiplier


def google_exchange_candidates(symbol: str, exchange_hint: str) -> list[str]:
  upper = symbol.upper()
  candidates = []
  if upper.endswith(".NS"):
    candidates.append(f"{upper[:-3]}:NSE")
  elif upper.endswith(".BO"):
    candidates.append(f"{upper[:-3]}:BOM")
  elif upper.endswith(".AX"):
    candidates.append(f"{upper[:-3]}:ASX")
  elif upper.endswith(".L"):
    candidates.append(f"{upper[:-2]}:LON")
  elif upper.endswith(".T"):
    candidates.append(f"{upper[:-2]}:TYO")
  elif upper.endswith(".DE"):
    candidates.append(f"{upper[:-3]}:ETR")
  elif upper.startswith("^"):
    return []
  else:
    preferred = exchange_hint.upper()
    if preferred in {"NASDAQ", "NASDAQGS", "NASDAQGM", "NASDAQCM"}:
      candidates.extend([f"{upper}:NASDAQ", f"{upper}:NYSE"])
    elif preferred in {"NYSE", "NYSEARCA", "NYSEAMERICAN"}:
      candidates.extend([f"{upper}:NYSE", f"{upper}:NASDAQ"])
    else:
      candidates.extend([f"{upper}:NASDAQ", f"{upper}:NYSE"])
  return list(dict.fromkeys(candidates))


def extract_stat_after(lines: list[str], label: str, window: int = 4) -> str | None:
  lowered = label.lower()
  strict_value_pattern = re.compile(
    r"^(?:[₹$€£¥]\s*)?-?[\d,]+(?:\.\d+)?(?:\s*-\s*(?:[₹$€£¥]\s*)?[\d,]+(?:\.\d+)?)?(?:\s*[KMBT%])?(?:\s+[A-Z]{3})?$"
  )
  for index, line in enumerate(lines):
    if line.lower() == lowered:
      loose_candidate = None
      for candidate in lines[index + 1:index + 1 + window]:
        normalized = candidate.lower()
        if not candidate or normalized == lowered:
          continue
        if strict_value_pattern.match(candidate):
          return candidate
        if loose_candidate is None and len(candidate) <= 32 and re.search(r"[\d₹$€£¥%KMBT]", candidate):
          loose_candidate = candidate
      if loose_candidate:
        return loose_candidate
  return None


def fetch_google_finance_quote(symbol: str, exchange_hint: str = "") -> dict:
  for google_symbol in google_exchange_candidates(symbol, exchange_hint):
    html_text = text_get(f"https://www.google.com/finance/quote/{urllib.parse.quote(google_symbol)}")
    if not html_text:
      continue
    lines = visible_text_lines(html_text)
    if not lines:
      continue

    symbol_anchor = google_symbol.replace(":", " • ")
    anchor_index = next((index for index, line in enumerate(lines[:120]) if symbol_anchor in line), -1)
    if anchor_index < 0:
      symbol_base = google_symbol.split(":")[0]
      exchange_base = google_symbol.split(":")[1]
      anchor_index = next(
        (index for index, line in enumerate(lines[:120]) if symbol_base in line and exchange_base in line),
        -1,
      )
    if anchor_index < 0:
      continue

    window = lines[anchor_index:anchor_index + 16]
    name = next(
      (
        line for line in window[1:]
        if not re.search(r"[₹$€£¥]|^[\d,]+(?:\.\d+)?$", line)
        and "·" not in line
        and line not in {"1D", "5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX", "No data", "close"}
      ),
      fallback_meta(symbol)["name"],
    )

    price_text = next((line for line in window if re.search(r"[₹$€£¥]\s*[\d,]+(?:\.\d+)?", line)), "")
    if not price_text:
      continue
    price = parse_number(price_text)
    if price is None:
      continue

    timestamp_line = next((line for line in window if "·" in line and "Disclaimer" in line), "")
    currency_match = re.search(r"·\s*([A-Z]{3})\s*·", timestamp_line)
    exchange_match = re.search(r"·\s*[A-Z]{3}\s*·\s*([A-Z]+)", timestamp_line)
    currency = currency_match.group(1) if currency_match else fallback_meta(symbol)["currency"]
    exchange = exchange_match.group(1) if exchange_match else exchange_hint or fallback_meta(symbol)["exchange"]
    previous_close = parse_number(extract_stat_after(lines, "Previous close") or "")
    avg_volume = parse_compact_number(extract_stat_after(lines, "Avg Volume") or "")
    trailing_pe = parse_number(extract_stat_after(lines, "P/E ratio") or "")
    market_cap = parse_compact_number(extract_stat_after(lines, "Market cap") or "")
    day_range = extract_stat_after(lines, "Day range") or ""
    low_high = re.findall(r"[\d,]+(?:\.\d+)?", day_range)
    fifty_two_week = extract_stat_after(lines, "Year range") or ""
    year_low_high = re.findall(r"[\d,]+(?:\.\d+)?", fifty_two_week)

    return {
      "symbol": symbol,
      "shortName": name,
      "longName": name,
      "regularMarketPrice": price,
      "regularMarketPreviousClose": previous_close,
      "regularMarketChangePercent": pct_change(price, previous_close) if previous_close else 0.0,
      "averageDailyVolume3Month": int(avg_volume or 0),
      "regularMarketVolume": 0,
      "trailingPE": trailing_pe,
      "marketCap": market_cap,
      "currency": currency,
      "exchange": exchange,
      "fullExchangeName": exchange,
      "marketState": "REGULAR",
      "fiftyTwoWeekLow": parse_number(year_low_high[0]) if len(year_low_high) >= 2 else None,
      "fiftyTwoWeekHigh": parse_number(year_low_high[1]) if len(year_low_high) >= 2 else None,
      "dayLow": parse_number(low_high[0]) if len(low_high) >= 2 else None,
      "dayHigh": parse_number(low_high[1]) if len(low_high) >= 2 else None,
      "quoteSource": "Google Finance",
    }
  return {}


def extract_balanced_array(text: str, start: int) -> str | None:
  depth = 0
  in_string = False
  escape = False
  for index in range(start, len(text)):
    char = text[index]
    if in_string:
      if escape:
        escape = False
      elif char == "\\":
        escape = True
      elif char == '"':
        in_string = False
      continue
    if char == '"':
      in_string = True
    elif char == "[":
      depth += 1
    elif char == "]":
      depth -= 1
      if depth == 0:
        return text[start:index + 1]
  return None


def extract_google_finance_series(html_text: str) -> list[list]:
  series = []
  for match in re.finditer(r"\[\[\[\d{4},\d{1,2},\d{1,2}", html_text):
    payload = extract_balanced_array(html_text, match.start())
    if not payload:
      continue
    try:
      data = json.loads(payload)
    except json.JSONDecodeError:
      continue
    if not isinstance(data, list) or len(data) < 2:
      continue
    if not all(isinstance(item, list) and len(item) >= 2 for item in data[:2]):
      continue
    series.append(data)
  return series


def normalize_google_finance_history(series: list, chart_range: str) -> list[float]:
  normalized_range = chart_range.upper()
  intraday = []
  multi_day = []
  for candidate in series:
    closes = []
    dates = set()
    for item in candidate:
      if not isinstance(item, list) or len(item) < 2:
        continue
      timestamp_block = item[0]
      price_block = item[1]
      if not isinstance(timestamp_block, list) or len(timestamp_block) < 3:
        continue
      if not isinstance(price_block, list) or not price_block:
        continue
      price = price_block[0]
      if not isinstance(price, (int, float)):
        continue
      closes.append(float(price))
      dates.add(tuple(timestamp_block[:3]))
    if len(closes) < 2:
      continue
    if len(dates) <= 2:
      intraday.append(closes)
    else:
      multi_day.append(closes)

  if normalized_range == "1D":
    return max(intraday, key=len, default=(max(multi_day, key=len, default=[])))
  if normalized_range in {"3D", "5D"}:
    base = max(multi_day, key=len, default=[])
    keep = 3 if normalized_range == "3D" else 5
    return base[-keep:] if len(base) >= 2 else max(intraday, key=len, default=[])
  if normalized_range in {"1M", "1Y"}:
    return max(multi_day, key=len, default=(max(intraday, key=len, default=[])))
  return max(multi_day, key=len, default=(max(intraday, key=len, default=[])))


def fetch_google_finance_history(symbol: str, exchange_hint: str = "", chart_range: str = "1M") -> tuple[list[float], dict]:
  for google_symbol in google_exchange_candidates(symbol, exchange_hint):
    html_text = text_get(f"https://www.google.com/finance/quote/{urllib.parse.quote(google_symbol)}")
    if not html_text:
      continue
    series = extract_google_finance_series(html_text)
    closes = normalize_google_finance_history(series, chart_range)
    if len(closes) >= 2:
      return closes, {
        "historySource": "Google Finance Page",
        "googleSymbol": google_symbol,
      }
  return [], {}


def fetch_live_quotes(symbols: list[str]) -> dict[str, dict]:
  primary = fetch_yahoo_quotes(symbols)
  missing = [symbol for symbol in symbols if symbol.upper() not in primary]
  if not missing:
    return primary

  with ThreadPoolExecutor(max_workers=min(4, len(missing))) as executor:
    futures = {
      executor.submit(fetch_google_finance_quote, symbol, fallback_meta(symbol).get("exchange", "")): symbol
      for symbol in missing
    }
    for future, symbol in futures.items():
      try:
        quote = future.result()
      except Exception:
        quote = {}
      if quote:
        primary[symbol.upper()] = quote
  return primary


def post_json(url: str, payload: dict, timeout: int = 40) -> dict | None:
  data = json.dumps(payload).encode("utf-8")
  request = urllib.request.Request(
    url,
    data=data,
    headers={
      "User-Agent": USER_AGENT,
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
  )
  try:
    with urllib.request.urlopen(request, timeout=timeout) as response:
      return json.loads(response.read().decode("utf-8"))
  except Exception:
    return None


def normalize_symbol(symbol: str, market: str | None = None) -> str:
  cleaned = (symbol or "").strip().upper()
  if not cleaned:
    return ""
  if cleaned.startswith("^") or cleaned.endswith("=F") or cleaned.endswith("-USD"):
    return cleaned
  if "." in cleaned:
    return cleaned
  suffix = MARKET_SUFFIXES.get((market or "").lower(), "")
  return f"{cleaned}{suffix}"


def deterministic_noise(seed: int, index: int) -> float:
  value = math.sin(seed * 0.017 + index * 0.83) * 10000
  return value - math.floor(value)


def symbol_seed(symbol: str) -> int:
  return sum(ord(char) * (index + 11) for index, char in enumerate(symbol))


def fallback_meta(symbol: str) -> dict:
  if symbol in FALLBACK_TICKERS:
    return FALLBACK_TICKERS[symbol]
  if symbol.endswith(".NS"):
    return {"name": symbol.replace(".NS", ""), "basePrice": 1200.0, "currency": "INR", "exchange": "NSE", "beta": 0.92, "pe": 24.0}
  if symbol.endswith(".BO"):
    return {"name": symbol.replace(".BO", ""), "basePrice": 1200.0, "currency": "INR", "exchange": "BSE", "beta": 0.92, "pe": 24.0}
  if symbol.endswith(".AX"):
    return {"name": symbol.replace(".AX", ""), "basePrice": 38.0, "currency": "AUD", "exchange": "ASX", "beta": 0.86, "pe": 17.0}
  if symbol.endswith(".T"):
    return {"name": symbol.replace(".T", ""), "basePrice": 3150.0, "currency": "JPY", "exchange": "JPX", "beta": 0.78, "pe": 15.0}
  if symbol.startswith("^"):
    return {"name": symbol, "basePrice": 100.0, "currency": "USD", "exchange": "Index", "beta": 1.0, "pe": 20.0}
  return {"name": symbol, "basePrice": 120.0 + (symbol_seed(symbol) % 180), "currency": "USD", "exchange": "US", "beta": 1.0, "pe": 22.0}


def fallback_series(symbol: str, points: int = 180) -> list[float]:
  meta = fallback_meta(symbol)
  base_price = meta["basePrice"]
  drift = ((symbol_seed(symbol) % 13) - 6) / 2800
  cycle = ((symbol_seed(symbol) % 7) + 3) / 40
  beta = meta["beta"]
  price = float(base_price)
  series = []
  for index in range(points):
    seasonal = math.sin(index / cycle) * price * 0.008
    shock = (deterministic_noise(symbol_seed(symbol), index) - 0.48) * price * 0.012 * beta
    price = max(price + price * drift + seasonal + shock, 1)
    series.append(round(price, 2))
  return series


def average(values: list[float]) -> float:
  if not values:
    return 0.0
  return sum(values) / len(values)


def std_dev(values: list[float]) -> float:
  if len(values) < 2:
    return 0.0
  return statistics.pstdev(values)


def pct_change(current: float, previous: float) -> float:
  if not previous:
    return 0.0
  return ((current - previous) / previous) * 100


def format_large_number(value: float | int | None) -> str:
  if value in (None, ""):
    return "n/a"
  number = float(value)
  for threshold, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
    if abs(number) >= threshold:
      return f"{number / threshold:.2f}{suffix}"
  return f"{number:.0f}"


def fetch_yahoo_quotes(symbols: list[str]) -> dict[str, dict]:
  cleaned = [symbol for symbol in symbols if symbol]
  if not cleaned:
    return {}
  quoted = urllib.parse.quote(",".join(cleaned))
  payload = json_get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={quoted}")
  results = {}
  quote_response = (payload or {}).get("quoteResponse", {})
  for item in quote_response.get("result", []):
    symbol = item.get("symbol")
    if symbol:
      results[symbol.upper()] = item
  return results


def fetch_yahoo_chart(symbol: str, range_value: str = "6mo", interval: str = "1d") -> dict | None:
  quoted = urllib.parse.quote(symbol)
  payload = json_get(
    f"https://query1.finance.yahoo.com/v8/finance/chart/{quoted}?range={range_value}&interval={interval}&includePrePost=false&events=div%2Csplits"
  )
  chart = (payload or {}).get("chart", {})
  results = chart.get("result", [])
  return results[0] if results else None


def fetch_yahoo_quote_summary(symbol: str) -> dict:
  quoted = urllib.parse.quote(symbol)
  payload = json_get(
    f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{quoted}?modules=summaryDetail,defaultKeyStatistics,financialData,assetProfile"
  )
  result = ((payload or {}).get("quoteSummary") or {}).get("result") or []
  return result[0] if result else {}


def local_search_results(query: str) -> list[dict]:
  cleaned = query.strip().upper()
  if not cleaned:
    return []
  results = []
  for symbol, meta in FALLBACK_TICKERS.items():
    normalized_name = meta["name"].upper()
    if (
      cleaned in symbol
      or cleaned in normalized_name
      or cleaned == symbol.replace(".NS", "")
      or cleaned == symbol.replace(".BO", "")
    ):
      results.append(
        {
          "symbol": symbol,
          "name": meta["name"],
          "exchange": meta["exchange"],
          "region": meta["exchange"],
        }
      )
  return results


def ranked_results(query: str, remote_results: list[dict]) -> list[dict]:
  local_results = local_search_results(query)
  seen = set()
  ordered = []

  def push(item: dict) -> None:
    symbol = item.get("symbol", "").upper()
    if not symbol or symbol in seen:
      return
    seen.add(symbol)
    ordered.append(item)

  cleaned = query.strip().upper()
  for item in local_results:
    push(item)
  for item in remote_results:
    push(item)

  ordered.sort(
    key=lambda item: (
      0 if item["symbol"].upper() == cleaned else 1,
      0 if item["symbol"].upper() == f"{cleaned}.NS" else 1,
      0 if item.get("exchange") == "NSE" else 1,
      item["symbol"],
    )
  )
  return ordered[:10]


def fetch_yahoo_search(query: str) -> list[dict]:
  quoted = urllib.parse.quote(query)
  payload = json_get(
    f"https://query1.finance.yahoo.com/v1/finance/search?q={quoted}&quotesCount=10&newsCount=0"
  )
  results = []
  for item in (payload or {}).get("quotes", []):
    symbol = item.get("symbol")
    if not symbol:
      continue
    results.append(
      {
        "symbol": symbol.upper(),
        "name": item.get("shortname") or item.get("longname") or symbol,
        "exchange": item.get("exchange") or item.get("exchDisp") or "",
        "region": item.get("exchange") or "",
      }
    )
  return ranked_results(query, results)


def duckduckgo_search(query: str) -> list[dict]:
  quoted = urllib.parse.quote(query)
  html_text = text_get(f"https://duckduckgo.com/html/?q={quoted}")
  if not html_text:
    return []

  matches = re.findall(
    r'<a[^>]*class="result__a"[^>]*href="(?P<href>[^"]+)"[^>]*>(?P<title>.*?)</a>',
    html_text,
    flags=re.IGNORECASE | re.DOTALL,
  )

  results = []
  for href, title_html in matches[:6]:
    title = html.unescape(re.sub(r"<.*?>", "", title_html)).strip()
    url = html.unescape(href)
    if "uddg=" in url:
      parsed = urllib.parse.urlparse(url)
      nested = urllib.parse.parse_qs(parsed.query).get("uddg")
      if nested:
        url = urllib.parse.unquote(nested[0])
    results.append({"title": title or "Result", "url": url})
  return results


def generate_local_llm_answer(prompt: str, config: dict) -> str | None:
  base = (config.get("localLlmBaseUrl") or DEFAULT_CONFIG["localLlmBaseUrl"]).rstrip("/")
  model = config.get("localLlmModel") or DEFAULT_CONFIG["localLlmModel"]
  payload = {
    "model": model,
    "stream": False,
    "prompt": prompt,
    "options": {"temperature": 0.2},
  }
  response = post_json(f"{base}/api/generate", payload)
  if not response:
    return None
  return (response.get("response") or "").strip() or None


def build_research_context(symbol: str | None) -> dict:
  if not symbol:
    return {"symbol": "", "summary": "No active ticker selected."}
  snapshot = build_ticker_snapshot(symbol)
  return {
    "symbol": snapshot["symbol"],
    "name": snapshot["name"],
    "currency": snapshot["currency"],
    "price": snapshot["price"],
    "changePercent": snapshot["changePercent"],
    "regime": snapshot["regime"],
    "forecast": snapshot["forecast"]["direction"],
    "confidence": round(snapshot["forecast"]["confidence"], 1),
    "fairValueGap": round(snapshot["forecast"]["fairValueGap"], 2),
    "volume": snapshot["volume"],
    "stats": snapshot["stats"],
    "triggers": snapshot["forecast"]["triggers"],
  }


def synthesize_without_llm(query: str, context: dict, web_results: list[dict]) -> str:
  pieces = []
  if context.get("symbol"):
    pieces.append(
      f"{context['symbol']} is trading in {context.get('currency', 'local currency')} with a {context.get('forecast', 'neutral')} forecast, {context.get('confidence', 0)}% confidence, and fair-value gap of {context.get('fairValueGap', 0)}%."
    )
  if web_results:
    pieces.append("Web search found recent external references that may help ground the answer.")
  pieces.append(f"Question: {query}")
  pieces.append("Use the forecast, volume, catalysts, and any search results together before acting.")
  return " ".join(pieces)


def run_research_agent(query: str, symbol: str | None, use_web: bool, use_llm: bool) -> dict:
  config = load_config()
  context = {}
  web_results: list[dict] = []

  with ThreadPoolExecutor(max_workers=2) as executor:
    context_future = executor.submit(build_research_context, symbol)
    web_future = executor.submit(duckduckgo_search, query) if use_web else None
    context = context_future.result()
    if web_future is not None:
      web_results = web_future.result()

  prompt = "\n".join(
    [
      "You are a concise market research assistant embedded in a financial dashboard.",
      "Answer using the dashboard context first, then use the web results only as supporting evidence.",
      "Do not fabricate citations. If web results are weak, say so.",
      f"User question: {query}",
      f"Dashboard context: {json.dumps(context, ensure_ascii=True)}",
      f"Web results: {json.dumps(web_results, ensure_ascii=True)}",
      "Return a short answer, then 3-5 bullets of key takeaways.",
    ]
  )

  answer = generate_local_llm_answer(prompt, config) if use_llm else None
  if not answer:
    answer = synthesize_without_llm(query, context, web_results)

  takeaways = []
  for trigger in (context.get("triggers") or [])[:4]:
    takeaways.append(trigger.get("body"))

  return {
    "answer": answer,
    "webResults": web_results,
    "context": context,
    "takeaways": [item for item in takeaways if item][:4],
    "llmUsed": bool(use_llm and answer and "Question:" not in answer),
  }


def build_event_feed(category: str, symbol: str | None = None, keyword: str | None = None) -> dict:
  normalized = (category or "business").strip().lower()
  if normalized not in EVENT_CATEGORY_QUERIES:
    normalized = "business"
  symbol_query = ""
  if symbol:
    symbol_meta = fallback_meta(symbol)
    symbol_query = f" {symbol_meta['name']} {symbol_meta['exchange']}"
  query = (keyword or "").strip() or f"{EVENT_CATEGORY_QUERIES[normalized]}{symbol_query}"
  results = duckduckgo_search(query)

  titles = [item.get("title", "") for item in results if item.get("title")]
  if symbol and normalized in {"partnerships", "deals", "brands", "layoffs"}:
    company_meta = fallback_meta(symbol)
    company_results = duckduckgo_search(f"{company_meta['name']} {normalized} latest news")
    extra = [item for item in company_results if item.get("url") not in {result.get("url") for result in results}]
    results = (results + extra)[:8]
    titles = [item.get("title", "") for item in results if item.get("title")]

  config = load_config()
  brief = ""
  if titles:
    prompt = "\n".join(
      [
        "You are a concise event-briefing assistant inside a market dashboard.",
        f"Category: {normalized}",
        f"Symbol: {symbol or 'none'}",
        f"Headlines: {json.dumps(titles[:6], ensure_ascii=True)}",
        "Write one compact sentence summarizing the event flow and what kind of market risk it signals.",
      ]
    )
    brief = generate_local_llm_answer(prompt, config) or ""

  if not brief:
    brief = (
      f"{normalized.title()} flow is quiet right now."
      if not titles
      else f"{normalized.title()} headlines are active, with the latest results skewing toward market-relevant updates."
    )

  return {
    "category": normalized,
    "query": query,
    "brief": brief,
    "items": results[:8],
  }


def infer_radar_hotspots(items: list[dict]) -> list[dict]:
  scores: dict[str, dict] = {}
  for item in items:
    title = (item.get("title") or "").lower()
    if not title:
      continue
    for region, keywords in RADAR_REGION_KEYWORDS.items():
      matches = sum(1 for keyword in keywords if keyword in title)
      if not matches:
        continue
      current = scores.setdefault(region, {"region": region, "score": 0, "headline": item.get("title", "")})
      current["score"] += matches
      if not current.get("headline"):
        current["headline"] = item.get("title", "")
  ordered = sorted(scores.values(), key=lambda item: item["score"], reverse=True)
  return ordered[:4]


def build_market_radar(symbol: str | None = None) -> dict:
  queries = [
    EVENT_CATEGORY_QUERIES["world"],
    EVENT_CATEGORY_QUERIES["war"],
    EVENT_CATEGORY_QUERIES["business"],
  ]
  if symbol:
    company = fallback_meta(symbol)
    queries.append(f"{company['name']} latest news {company['exchange']}")

  items: list[dict] = []
  for query in queries:
    items.extend(duckduckgo_search(query))
  unique_items = []
  seen_urls = set()
  for item in items:
    url = item.get("url")
    if not url or url in seen_urls:
      continue
    seen_urls.add(url)
    unique_items.append(item)

  hotspots = infer_radar_hotspots(unique_items)
  titles = [item.get("title", "") for item in unique_items[:6] if item.get("title")]
  config = load_config()
  summary = ""
  if titles:
    prompt = "\n".join(
      [
        "You are a concise global market radar assistant.",
        f"Headlines: {json.dumps(titles, ensure_ascii=True)}",
        f"Hotspots: {json.dumps(hotspots, ensure_ascii=True)}",
        "Write one compact market-risk summary sentence, focused on what geographies are driving sentiment and why markets care.",
      ]
    )
    summary = generate_local_llm_answer(prompt, config) or ""
  if not summary:
    summary = "Global event radar is scanning live developments across geopolitics, business, and company-specific catalysts."

  return {
    "summary": summary,
    "headlines": titles[:6],
    "hotspots": hotspots,
    "items": unique_items[:6],
  }


def fetch_yahoo_rss(symbol: str) -> list[str]:
  quoted = urllib.parse.quote(symbol)
  xml_text = text_get(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={quoted}&region=US&lang=en-US")
  if not xml_text:
    return []
  try:
    root = ET.fromstring(xml_text)
  except ET.ParseError:
    return []
  items = []
  for item in root.findall(".//item/title"):
    if item.text:
      items.append(item.text.strip())
    if len(items) >= 6:
      break
  return items


def fetch_alpha_vantage_news(symbol: str, api_key: str) -> list[str]:
  if not api_key:
    return []
  query = urllib.parse.urlencode(
    {
      "function": "NEWS_SENTIMENT",
      "tickers": symbol,
      "limit": "8",
      "apikey": api_key,
    }
  )
  payload = json_get(f"https://www.alphavantage.co/query?{query}")
  items = []
  for story in (payload or {}).get("feed", []):
    title = story.get("title")
    if title:
      items.append(title)
  return items[:6]


def headline_texts_from_search(query: str) -> list[str]:
  return [item.get("title", "") for item in duckduckgo_search(query)[:6] if item.get("title")]


def dedupe_list(items: list[str]) -> list[str]:
  seen = set()
  ordered = []
  for item in items:
    cleaned = item.strip()
    if not cleaned:
      continue
    key = cleaned.lower()
    if key in seen:
      continue
    seen.add(key)
    ordered.append(cleaned)
  return ordered


def headline_sentiment(headlines: list[str]) -> dict:
  positive_words = {
    "beats", "beat", "growth", "surge", "rally", "approval", "wins", "win", "partnership",
    "contract", "upgrade", "record", "strong", "expansion", "launch", "profit", "optimism",
  }
  negative_words = {
    "cuts", "cut", "probe", "lawsuit", "downgrade", "fall", "drop", "warning", "miss", "delay",
    "ban", "fine", "weak", "slump", "decline", "recall", "antitrust", "risk",
  }
  text = " ".join(headlines).lower()
  pos = sum(word in text for word in positive_words)
  neg = sum(word in text for word in negative_words)
  score = clamp((pos - neg) / max(len(headlines), 1), -1.0, 1.0)
  label = "Positive" if score > 0.22 else "Negative" if score < -0.22 else "Mixed"
  return {"score": score, "label": label, "positiveHits": pos, "negativeHits": neg}


def categorized_signal(headlines: list[str], keywords: set[str], fallback_label: str) -> dict:
  for headline in headlines:
    lowered = headline.lower()
    if any(keyword in lowered for keyword in keywords):
      return {"label": fallback_label, "headline": headline}
  return {"label": fallback_label, "headline": "No strong current signal detected."}


def extract_signal_map(headlines: list[str], symbol: str, sector: str, industry: str) -> dict:
  policy = categorized_signal(
    headlines,
    {
      "government", "policy", "rbi", "fed", "budget", "tariff", "tax", "regulator", "regulatory",
      "parliament", "ministry", "sec", "fda", "approval", "probe", "ban",
    },
    "Policy & regulation",
  )
  deals = categorized_signal(
    headlines,
    {
      "deal", "partnership", "contract", "agreement", "collaboration", "alliance", "order",
      "acquire", "acquisition", "merger", "stake", "joint venture",
    },
    "Deals & partnerships",
  )
  industry_signal = categorized_signal(
    headlines,
    {
      "sector", "industry", "demand", "supply", "pricing", "competitor", "telecom", "bank", "pharma",
      "credit", "subscriber", "tower", "generic", "energy", "chip", "semiconductor",
    },
    "Adjacent industry",
  )
  earnings = categorized_signal(
    headlines,
    {"earnings", "revenue", "profit", "margin", "guidance", "results", "ebitda", "quarter"},
    "Financial results",
  )
  sentiment = headline_sentiment(headlines)
  return {
    "sentiment": sentiment,
    "signals": [policy, deals, industry_signal, earnings],
    "sector": sector or "n/a",
    "industry": industry or "n/a",
    "symbol": symbol,
  }


CHART_RANGE_CONFIG = {
  "1D": ("1d", "5m"),
  "3D": ("5d", "15m"),
  "5D": ("5d", "30m"),
  "1M": ("1mo", "1d"),
  "1Y": ("1y", "1wk"),
}


def build_history(symbol: str, chart_range: str = "1M") -> tuple[list[float], dict]:
  normalized_range = chart_range.upper()
  cached = load_cached_history(symbol, normalized_range)
  if cached:
    closes, meta, source, updated_at = cached
    try:
      age_seconds = max(
        0,
        (datetime.now(timezone.utc) - datetime.fromisoformat(updated_at)).total_seconds(),
      )
    except ValueError:
      age_seconds = history_cache_ttl(normalized_range) + 1
    if len(closes) >= 2 and age_seconds <= history_cache_ttl(normalized_range):
      return closes, build_cached_meta(meta, source or "Local cache", updated_at)

  range_value, interval = CHART_RANGE_CONFIG.get(normalized_range, CHART_RANGE_CONFIG["1M"])
  chart = fetch_yahoo_chart(symbol, range_value=range_value, interval=interval)
  if chart:
    quote_indicator = (((chart.get("indicators") or {}).get("quote") or [{}])[0] or {})
    closes = [value for value in (quote_indicator.get("close") or []) if isinstance(value, (int, float))]
    meta = chart.get("meta") or {}
    if len(closes) >= 2:
      save_history_cache(symbol, normalized_range, closes, meta, "Yahoo Chart")
      return closes, build_cached_meta(meta, "Yahoo Chart", datetime.now(timezone.utc).isoformat())

  google_closes, google_meta = fetch_google_finance_history(symbol, fallback_meta(symbol).get("exchange", ""), normalized_range)
  if len(google_closes) >= 2:
    save_history_cache(symbol, normalized_range, google_closes, google_meta, google_meta.get("historySource", "Google Finance Page"))
    return google_closes, build_cached_meta(
      google_meta,
      google_meta.get("historySource", "Google Finance Page"),
      datetime.now(timezone.utc).isoformat(),
    )

  if cached:
    closes, meta, source, updated_at = cached
    if len(closes) >= 2:
      return closes, build_cached_meta(meta, source or "Local cache", updated_at, stale=True)
  return [], {}


def build_forecast_inputs(symbol: str, quote: dict, summary: dict, history: list[float], news_count: int) -> dict:
  previous_close = float(quote.get("regularMarketPreviousClose") or history[-2] or history[-1])
  latest_price = float(quote.get("regularMarketPrice") or history[-1])
  change_pct = float(quote.get("regularMarketChangePercent") or pct_change(latest_price, previous_close))

  summary_detail = summary.get("summaryDetail") or {}
  statistics_block = summary.get("defaultKeyStatistics") or {}
  financial_data = summary.get("financialData") or {}

  beta = (
    statistics_block.get("beta", {}).get("raw")
    or summary_detail.get("beta", {}).get("raw")
    or fallback_meta(symbol)["beta"]
  )
  pe_ratio = (
    quote.get("trailingPE")
    or summary_detail.get("trailingPE", {}).get("raw")
    or fallback_meta(symbol)["pe"]
  )
  market_cap = quote.get("marketCap") or financial_data.get("marketCap", {}).get("raw") or 0
  quality_score = clamp(
    0.35
    + min(math.log10(market_cap + 1) / 15, 0.22)
    + (0.08 if float(pe_ratio or 0) < 28 else 0.0),
    0.32,
    0.88,
  )
  event_score = clamp(abs(change_pct) / 8 + news_count * 0.05, 0.22, 0.96)

  return {
    "latestPrice": latest_price,
    "previousPrice": previous_close,
    "beta": float(beta),
    "pe": float(pe_ratio or 20.0),
    "qualityScore": quality_score,
    "eventScore": event_score,
    "marketCap": market_cap,
  }


def build_macro_score(region: str, beta: float, pe_ratio: float, stress: str) -> float:
  base = (beta - 1) * -0.06 + (-0.02 if pe_ratio > 30 else 0.04)
  if "India" in region:
    base += 0.01
  shock_map = {
    "base": 0.0,
    "riskoff": -0.18,
    "growth": 0.16,
    "inflation": -0.07 if "US" in region else -0.03,
  }
  return base + shock_map.get(stress, 0.0)


def infer_regime(macro_score: float, realized_vol: float, event_score: float) -> str:
  if realized_vol > 0.03 or event_score > 0.72:
    return "High-volatility event regime"
  if macro_score > 0.08:
    return "Growth acceleration regime"
  if macro_score < -0.08:
    return "Risk-off regime"
  return "Balanced regime"


def clamp(value: float, low: float, high: float) -> float:
  return max(low, min(high, value))


def build_factor_cards(inputs: dict) -> list[dict]:
  return [
    {
      "title": "Fast momentum",
      "score": clamp(inputs["fastMomentum"] * 1200, -100, 100),
      "description": "Short-horizon tape strength captures flow, positioning, and immediate momentum persistence.",
    },
    {
      "title": "Slow trend",
      "score": clamp(inputs["slowMomentum"] * 1600, -100, 100),
      "description": "The longer drift filter stops the model from overreacting to a single noisy session.",
    },
    {
      "title": "Mean reversion",
      "score": clamp(inputs["meanReversion"] * 700, -100, 100),
      "description": "If price stretches too far from its rolling center, continuation odds are discounted.",
    },
    {
      "title": "Macro carry-through",
      "score": clamp(inputs["macroScore"] * 420, -100, 100),
      "description": "Rates, growth, inflation, and index sensitivity are mapped into asset-specific headwinds or tailwinds.",
    },
    {
      "title": "Volatility tax",
      "score": clamp(-inputs["realizedVol"] * 2400, -100, 100),
      "description": "Higher realized volatility lowers confidence and increases expected forecast error.",
    },
    {
      "title": "Quality overlay",
      "score": clamp(inputs["qualityLift"] * 220, -100, 100),
      "description": "Steadier fundamentals keep the model from blindly chasing fragile momentum bursts.",
    },
  ]


def build_relationship_cards(snapshot_inputs: dict, signal_map: dict) -> list[dict]:
  volume_ratio = snapshot_inputs["volumeRatio"]
  return [
    {
      "title": "Valuation",
      "score": clamp((28 - snapshot_inputs["pe"]) * 3.5, -100, 100),
      "description": f"Trailing P/E at {snapshot_inputs['pe']:.2f}; used as a valuation pressure input rather than a standalone buy/sell rule.",
    },
    {
      "title": "Volume pulse",
      "score": clamp((volume_ratio - 1) * 75, -100, 100),
      "description": f"Current volume is {volume_ratio:.2f}x the reference average, which helps distinguish conviction from low-participation moves.",
    },
    {
      "title": "News sentiment",
      "score": clamp(signal_map["sentiment"]["score"] * 100, -100, 100),
      "description": f"Headline read is {signal_map['sentiment']['label'].lower()}, based on directional language in the latest catalyst set.",
    },
    {
      "title": "Policy risk",
      "score": 35 if signal_map["signals"][0]["headline"] != "No strong current signal detected." else 0,
      "description": signal_map["signals"][0]["headline"],
    },
    {
      "title": "Deal flow",
      "score": 32 if signal_map["signals"][1]["headline"] != "No strong current signal detected." else 0,
      "description": signal_map["signals"][1]["headline"],
    },
    {
      "title": "Adjacent industry",
      "score": 28 if signal_map["signals"][2]["headline"] != "No strong current signal detected." else 0,
      "description": signal_map["signals"][2]["headline"],
    },
  ]


def build_driver_cards(signal_map: dict, summary: dict, forecast: dict) -> list[dict]:
  sector = signal_map["sector"]
  industry = signal_map["industry"]
  cards = [
    {
      "title": "Sentiment pulse",
      "body": f"Current headline sentiment is {signal_map['sentiment']['label'].lower()}. This is used with volatility so sentiment alone does not dominate the forecast.",
      "tag": signal_map["sentiment"]["label"],
    },
    {
      "title": "Policy & regulation",
      "body": signal_map["signals"][0]["headline"],
      "tag": "Policy",
    },
    {
      "title": "Deals & partnerships",
      "body": signal_map["signals"][1]["headline"],
      "tag": "Deal flow",
    },
    {
      "title": "Adjacent industry",
      "body": f"{signal_map['signals'][2]['headline']} Sector context: {sector}. Industry context: {industry}.",
      "tag": "Industry",
    },
    {
      "title": "Forecast relationship",
      "body": f"The current forecast is {forecast['direction'].lower()} with {forecast['confidence']:.0f}% confidence and {forecast['eventPressureLabel'].lower()} event pressure.",
      "tag": "Model",
    },
  ]
  return cards


def build_triggers(inputs: dict, stress: str) -> list[dict]:
  return [
    {
      "title": "Trend alignment",
      "body": (
        "Short and medium-term trends are both positive, which improves continuation odds."
        if inputs["fastMomentum"] > 0 and inputs["slowMomentum"] > 0
        else "Short and medium-term trends disagree, which lowers conviction."
      ),
    },
    {
      "title": "Macro linkage",
      "body": (
        "Current macro conditions support this style exposure and region."
        if inputs["macroScore"] > 0
        else "Top-down conditions are acting as a drag, so stock-specific strength is discounted."
      ),
    },
    {
      "title": "Volatility impact",
      "body": (
        "Realized volatility is elevated, so model error and stop-out risk both rise."
        if inputs["realizedVol"] > 0.025
        else "Volatility remains contained enough for confidence to stay relatively stable."
      ),
    },
    {
      "title": "Stretch check",
      "body": (
        "Price is materially stretched versus its recent center, increasing snap-back risk."
        if abs(inputs["meanReversion"]) > 0.04
        else "Price is not excessively stretched, so continuation remains plausible."
      ),
    },
    {
      "title": "Stress lens",
      "body": f"The {stress} scenario changes macro weights without changing the observed price path, separating regime risk from ticker-specific behavior.",
    },
  ]


def build_forecast(symbol: str, quote: dict, summary: dict, history: list[float], stress: str = "base", horizon: int = 10, news_count: int = 0) -> dict:
  if len(history) < 2:
    latest_price = float(quote.get("regularMarketPrice") or fallback_meta(symbol)["basePrice"])
    previous_close = float(quote.get("regularMarketPreviousClose") or latest_price)
    expected_return = pct_change(latest_price, previous_close) * 0.35
    projected = [round(latest_price, 2) for _ in range(horizon)]
    direction = "Bullish" if expected_return > 1 else "Bearish" if expected_return < -1 else "Neutral"
    return {
      "direction": direction,
      "confidence": 22.0,
      "fairValue": latest_price,
      "fairValueGap": 0.0,
      "eventPressure": 0.25,
      "eventPressureLabel": "Low",
      "mae": 0.0,
      "regime": "Live quote only",
      "expectedReturn": expected_return,
      "projected": projected,
      "realizedVol": 0.0,
      "factors": [],
      "triggers": [
        {
          "title": "History missing",
          "body": "A live quote is available, but the historical series could not be fetched from the current provider.",
        }
      ],
    }

  returns = [
    (history[index] - history[index - 1]) / history[index - 1]
    for index in range(1, len(history))
    if history[index - 1]
  ]
  recent_returns = returns[-20:] or returns or [0.0]
  enriched = build_forecast_inputs(symbol, quote, summary, history, news_count)

  fast_momentum = average((returns[-5:] or [0.0]))
  slow_momentum = average((returns[-20:] or [0.0]))
  mean_reversion = (average(history[-10:]) - enriched["latestPrice"]) / enriched["latestPrice"]
  realized_vol = std_dev(recent_returns)
  volatility_penalty = realized_vol * 1.6
  event_pressure = enriched["eventScore"] * 0.6 + realized_vol * 9
  region = quote.get("fullExchangeName") or quote.get("exchange") or "Global"
  macro_score = build_macro_score(region, enriched["beta"], enriched["pe"], stress)
  quality_lift = (enriched["qualityScore"] - 0.5) * 0.4

  factor_score = (
    fast_momentum * 1.4
    + slow_momentum * 1.2
    + mean_reversion * 0.9
    + macro_score * 0.8
    + quality_lift
    - volatility_penalty
    - event_pressure * 0.04
  )

  expected_return = factor_score * math.sqrt(horizon) * 100
  confidence = clamp(100 - realized_vol * 1600 - enriched["eventScore"] * 24, 18, 91)
  fair_value = enriched["latestPrice"] * (1 + factor_score * 1.65)
  mae = clamp(realized_vol * 100 * (1.7 + enriched["beta"] * 0.25), 1.6, 12.5)
  direction = "Bullish" if expected_return > 2 else "Bearish" if expected_return < -2 else "Neutral"
  regime = infer_regime(macro_score, realized_vol, enriched["eventScore"])

  projected = []
  cursor = enriched["latestPrice"]
  for step in range(1, horizon + 1):
    noise = (deterministic_noise(symbol_seed(symbol), step + 90) - 0.5) * realized_vol * 0.9
    cursor = cursor * (1 + factor_score / horizon + noise)
    projected.append(round(cursor, 2))

  factors = {
    "fastMomentum": fast_momentum,
    "slowMomentum": slow_momentum,
    "meanReversion": mean_reversion,
    "macroScore": macro_score,
    "realizedVol": realized_vol,
    "qualityLift": quality_lift,
  }

  return {
    "direction": direction,
    "confidence": confidence,
    "fairValue": fair_value,
    "fairValueGap": pct_change(fair_value, enriched["latestPrice"]),
    "eventPressure": event_pressure,
    "eventPressureLabel": "High" if event_pressure > 0.8 else "Medium" if event_pressure > 0.55 else "Low",
    "mae": mae,
    "regime": regime,
    "expectedReturn": expected_return,
    "projected": projected,
    "realizedVol": realized_vol,
    "factors": build_factor_cards(factors),
    "triggers": build_triggers(factors, stress),
  }


def build_backtest(symbol: str, history: list[float], quote: dict, summary: dict, horizon: int, stress: str, news_count: int) -> dict:
  minimum_history = max(12, horizon + 4)
  if len(history) < minimum_history:
    return {"mae": 0.0, "medianApe": 0.0, "hitRate": 0.0, "sampleCount": 0}

  errors = []
  hits = []
  start = max(6, min(24, len(history) // 3))
  end = len(history) - horizon
  minimum_window = max(6, horizon // 2 + 1)
  for index in range(start, end):
    window = history[:index]
    if len(window) < minimum_window:
      continue
    forecast = build_forecast(symbol, quote, summary, window, stress=stress, horizon=horizon, news_count=news_count)
    predicted = forecast["projected"][-1]
    actual = history[index + horizon - 1]
    current = window[-1]
    if not actual or not current:
      continue
    ape = abs((predicted - actual) / actual) * 100
    errors.append(ape)
    predicted_direction = 1 if predicted >= current else -1
    actual_direction = 1 if actual >= current else -1
    hits.append(1 if predicted_direction == actual_direction else 0)

  if not errors:
    return {"mae": 0.0, "medianApe": 0.0, "hitRate": 0.0, "sampleCount": 0}

  return {
    "mae": average(errors),
    "medianApe": statistics.median(errors),
    "hitRate": average(hits) * 100,
    "sampleCount": len(errors),
  }


def build_recommendation(forecast: dict) -> dict:
  confidence = float(forecast.get("confidence") or 0)
  expected_return = float(forecast.get("expectedReturn") or 0)
  fair_value_gap = float(forecast.get("fairValueGap") or 0)
  event_pressure = float(forecast.get("eventPressure") or 0)

  directional_edge = clamp((expected_return * 1.4) + (fair_value_gap * 0.65), -100, 100)
  buy = clamp(34 + directional_edge * 0.55 + confidence * 0.28 - event_pressure * 12, 0, 100)
  sell = clamp(34 - directional_edge * 0.55 + (event_pressure * 16) - confidence * 0.12, 0, 100)
  hold = clamp(100 - buy - sell, 0, 100)
  total = buy + sell + hold or 1
  buy = round((buy / total) * 100)
  sell = round((sell / total) * 100)
  hold = max(0, 100 - buy - sell)
  signal = "Buy bias" if buy >= max(sell, hold) else "Sell bias" if sell >= max(buy, hold) else "Hold bias"
  return {
    "buy": buy,
    "hold": hold,
    "sell": sell,
    "signal": signal,
  }


def build_ticker_snapshot(symbol: str, quote: dict | None = None, stress: str = "base", horizon: int = 10, chart_range: str = "1M") -> dict:
  quotes = fetch_live_quotes([symbol]) if quote is None else {symbol: quote}
  quote = quotes.get(symbol) or {}
  with ThreadPoolExecutor(max_workers=3) as executor:
    history_future = executor.submit(build_history, symbol, chart_range)
    summary_future = executor.submit(fetch_yahoo_quote_summary, symbol)
    rss_future = executor.submit(fetch_yahoo_rss, symbol)
    history, chart_meta = history_future.result()
    summary = summary_future.result()
  fallback = fallback_meta(symbol)
  config = load_config()
  headlines = []
  if config.get("provider") == "alpha_vantage" and config.get("alphaVantageApiKey"):
    headlines = fetch_alpha_vantage_news(symbol, config.get("alphaVantageApiKey", ""))
  if not headlines:
    headlines = rss_future.result()
  company_query = f"{fallback['name']} stock news {fallback['exchange']}"
  headlines = dedupe_list(headlines + headline_texts_from_search(company_query))
  news_count = len(headlines)

  model_history = history
  if len(model_history) < 70:
    longer_history, _ = build_history(symbol, "1Y")
    if len(longer_history) >= len(model_history):
      model_history = longer_history

  latest_price = float(quote.get("regularMarketPrice") or (history[-1] if history else fallback["basePrice"]))
  previous_close = float(quote.get("regularMarketPreviousClose") or (history[-2] if len(history) > 1 else latest_price))
  change_percent = float(quote.get("regularMarketChangePercent") or pct_change(latest_price, previous_close))
  forecast = build_forecast(symbol, quote, summary, model_history, stress=stress, horizon=horizon, news_count=news_count)
  backtest = build_backtest(symbol, model_history, quote, summary, horizon, stress, news_count)
  recommendation = build_recommendation(forecast)

  market_cap = quote.get("marketCap")
  trailing_pe = quote.get("trailingPE") or ((summary.get("summaryDetail") or {}).get("trailingPE") or {}).get("raw")
  fifty_two_week_low = quote.get("fiftyTwoWeekLow")
  fifty_two_week_high = quote.get("fiftyTwoWeekHigh")
  volume = quote.get("regularMarketVolume") or quote.get("averageDailyVolume3Month") or 0
  avg_volume = quote.get("averageDailyVolume3Month") or quote.get("averageDailyVolume10Day") or 0
  sector = ((summary.get("assetProfile") or {}).get("sector")) or fallback["exchange"]
  industry = ((summary.get("assetProfile") or {}).get("industry")) or fallback["name"]
  signal_map = extract_signal_map(headlines, symbol, sector, industry)
  volume_ratio = float(volume or 0) / float(avg_volume or volume or 1)
  data_source = quote.get("quoteSource") or ("Live source" if quote else "Fallback data")
  market_time = quote.get("regularMarketTime") or chart_meta.get("regularMarketTime")
  as_of = datetime.fromtimestamp(market_time, tz=timezone.utc).isoformat() if market_time else None

  relationship_inputs = {
    "pe": float(trailing_pe or fallback["pe"]),
    "volumeRatio": volume_ratio,
  }
  relationship_cards = build_relationship_cards(relationship_inputs, signal_map)
  driver_cards = build_driver_cards(signal_map, summary, forecast)

  return {
    "symbol": symbol,
    "name": quote.get("shortName") or quote.get("longName") or fallback["name"],
    "exchange": quote.get("fullExchangeName") or quote.get("exchange") or chart_meta.get("exchangeName") or fallback["exchange"],
    "region": quote.get("exchange") or fallback["exchange"],
    "currency": quote.get("currency") or chart_meta.get("currency") or fallback["currency"],
    "marketState": quote.get("marketState") or "REGULAR",
    "dataSource": data_source,
    "historySource": chart_meta.get("historySource") or "Unavailable",
    "historyCachedAt": chart_meta.get("historyCachedAt"),
    "historyCacheState": chart_meta.get("historyCacheState"),
    "asOf": as_of,
    "price": latest_price,
    "previousClose": previous_close,
    "changePercent": change_percent,
    "volume": int(volume or 0),
    "history": history,
    "sector": sector,
    "industry": industry,
    "regime": forecast["regime"],
    "forecast": forecast,
    "recommendation": recommendation,
    "chartRange": chart_range,
    "relationshipCards": relationship_cards,
    "driverCards": driver_cards,
    "sentiment": signal_map["sentiment"],
    "stats": [
      {"label": "Market cap", "value": format_large_number(market_cap)},
      {"label": "Trailing P/E", "value": f"{float(trailing_pe):.2f}" if trailing_pe else "n/a"},
      {"label": "Trade volume", "value": format_large_number(volume)},
      {"label": "Avg volume", "value": format_large_number(avg_volume)},
      {
        "label": "52W range",
        "value": (
          f"{float(fifty_two_week_low):.2f} - {float(fifty_two_week_high):.2f}"
          if fifty_two_week_low and fifty_two_week_high
          else "n/a"
        ),
      },
      {"label": "Backtest hit rate", "value": f"{backtest['hitRate']:.1f}%"},
    ],
    "headlines": headlines or FALLBACK_HEADLINES[:4],
    "lab": {
      "symbol": symbol,
      "history": history[-40:],
      "projected": forecast["projected"],
      "expectedReturn": forecast["expectedReturn"],
      "direction": forecast["direction"],
      "confidence": forecast["confidence"],
      "triggers": forecast["triggers"],
      "backtest": backtest,
      "historySource": chart_meta.get("historySource") or "Unavailable",
      "historyCachedAt": chart_meta.get("historyCachedAt"),
      "historyCacheState": chart_meta.get("historyCacheState"),
    },
  }


def build_macro_pulse() -> list[dict]:
  quotes = fetch_yahoo_quotes([item["symbol"] for item in MACRO_SYMBOLS])
  items = []
  for macro in MACRO_SYMBOLS:
    quote = quotes.get(macro["symbol"])
    if not quote:
      continue
    price = quote.get("regularMarketPrice")
    change = float(quote.get("regularMarketChangePercent") or 0)
    currency = quote.get("currency") or "USD"
    if price is None:
      continue
    value = f"{price:.2f}" if macro["symbol"] == "^TNX" else (
      f"{price:.2f}%" if macro["symbol"] == "^GSPC" and False else str(price)
    )
    if macro["symbol"] in {"CL=F", "GC=F"}:
      value = f"{price:.2f} {currency}"
    elif macro["symbol"] == "^TNX":
      value = f"{price/10:.2f}%"
    else:
      value = f"{price:.2f}"
    items.append(
      {
        "label": macro["label"],
        "value": value,
        "trend": f"{change:+.2f}%",
        "positive": change >= 0,
      }
    )
  return items or FALLBACK_MACRO_PULSE


def build_dashboard(symbols: list[str], active: str | None, chart_range: str = "1M") -> dict:
  cleaned = [symbol.upper() for symbol in symbols if symbol]
  if not cleaned:
    cleaned = DEFAULT_WATCHLIST.copy()
  if active and active.upper() not in cleaned:
    cleaned.insert(0, active.upper())
  cleaned = list(dict.fromkeys(cleaned))

  quote_map = fetch_live_quotes(cleaned)
  watchlist = []
  for symbol in cleaned:
    quote = quote_map.get(symbol, {})
    fallback = fallback_meta(symbol)
    history = None
    price = quote.get("regularMarketPrice")
    previous_close = quote.get("regularMarketPreviousClose")
    data_source = quote.get("quoteSource") or ("Live source" if quote else "Fallback data")
    if price is None or previous_close is None:
      history = build_history(symbol, chart_range)[0]
      if len(history) >= 2:
        price = history[-1]
        previous_close = history[-2]
        data_source = "History-derived"
      else:
        price = None
        previous_close = None
    watchlist.append(
      {
        "symbol": symbol,
        "name": quote.get("shortName") or quote.get("longName") or fallback["name"],
        "price": float(price) if price is not None else None,
        "changePercent": float(quote.get("regularMarketChangePercent") or pct_change(float(price), float(previous_close)) if price is not None and previous_close is not None else 0.0),
        "volume": int(quote.get("regularMarketVolume") or quote.get("averageDailyVolume3Month") or 0),
        "currency": quote.get("currency") or fallback["currency"],
        "exchange": quote.get("fullExchangeName") or quote.get("exchange") or fallback["exchange"],
        "dataSource": data_source,
      }
    )

  active_symbol = (active or cleaned[0]).upper()
  if active_symbol not in cleaned:
    active_symbol = cleaned[0]
  with ThreadPoolExecutor(max_workers=2) as executor:
    active_future = executor.submit(build_ticker_snapshot, active_symbol, quote_map.get(active_symbol), "base", 10, chart_range)
    macro_future = executor.submit(build_macro_pulse)
    radar_future = executor.submit(build_market_radar, active_symbol)
    active_snapshot = active_future.result()
    macro_pulse = macro_future.result()
    radar = radar_future.result()

  banner = radar["headlines"] or active_snapshot["headlines"][:4]

  return {
    "provider": load_config().get("provider", "yahoo"),
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "watchlist": watchlist,
    "active": active_snapshot,
    "macroPulse": macro_pulse,
    "radar": radar,
    "headlines": list(dict.fromkeys(banner))[:6],
  }


def build_live_quotes(symbols: list[str], active: str | None) -> dict:
  cleaned = [symbol.upper() for symbol in symbols if symbol]
  if not cleaned:
    cleaned = DEFAULT_WATCHLIST.copy()
  quote_map = fetch_live_quotes(cleaned)
  items = []
  active_item = None

  for symbol in cleaned:
    quote = quote_map.get(symbol, {})
    fallback = fallback_meta(symbol)
    history = None
    price = quote.get("regularMarketPrice")
    previous_close = quote.get("regularMarketPreviousClose")
    data_source = quote.get("quoteSource") or ("Live source" if quote else "Fallback data")
    if price is None or previous_close is None:
      history = build_history(symbol)[0]
      if len(history) >= 2:
        price = history[-1]
        previous_close = history[-2]
        data_source = "History-derived"
      else:
        price = None
        previous_close = None
    market_time = quote.get("regularMarketTime")
    item = {
      "symbol": symbol,
      "name": quote.get("shortName") or quote.get("longName") or fallback["name"],
      "price": float(price) if price is not None else None,
      "previousClose": float(previous_close) if previous_close is not None else None,
      "changePercent": float(quote.get("regularMarketChangePercent") or pct_change(float(price), float(previous_close)) if price is not None and previous_close is not None else 0.0),
      "volume": int(quote.get("regularMarketVolume") or quote.get("averageDailyVolume3Month") or 0),
      "currency": quote.get("currency") or fallback["currency"],
      "exchange": quote.get("fullExchangeName") or quote.get("exchange") or fallback["exchange"],
      "marketState": quote.get("marketState") or "REGULAR",
      "dataSource": data_source,
      "asOf": datetime.fromtimestamp(market_time, tz=timezone.utc).isoformat() if market_time else None,
    }
    items.append(item)
    if symbol == (active or cleaned[0]).upper():
      active_item = item

  return {
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "watchlist": items,
    "active": active_item or items[0],
  }


class FinancialBoardHandler(BaseHTTPRequestHandler):
  def do_GET(self) -> None:
    parsed = urllib.parse.urlparse(self.path)
    if parsed.path in {"/", "/index.html"}:
      return self.serve_file("index.html", "text/html; charset=utf-8")
    if parsed.path == "/styles.css":
      return self.serve_file("styles.css", "text/css; charset=utf-8")
    if parsed.path == "/app.js":
      return self.serve_file("app.js", "application/javascript; charset=utf-8")
    if parsed.path == "/api/health":
      return self.send_json({"status": "ok"})
    if parsed.path == "/api/config":
      return self.send_json(load_config())
    if parsed.path == "/api/presets":
      return self.send_json({"presets": MARKET_PRESETS, "research": RESEARCH_REFERENCES})
    if parsed.path == "/api/watchlists":
      return self.send_json({"watchlists": list_watchlists()})
    if parsed.path == "/api/academy":
      return self.send_json({"research": RESEARCH_REFERENCES})
    if parsed.path == "/api/events":
      params = urllib.parse.parse_qs(parsed.query)
      category = (params.get("category") or ["business"])[0]
      symbol = ((params.get("symbol") or [""])[0] or "").upper() or None
      keyword = (params.get("q") or [""])[0]
      return self.send_json(build_event_feed(category, symbol, keyword))
    if parsed.path == "/api/search":
      params = urllib.parse.parse_qs(parsed.query)
      query = (params.get("q") or [""])[0].strip()
      results = fetch_yahoo_search(query) if query else []
      if not results and query:
        results = [
          {
            "symbol": normalize_symbol(query, "nse"),
            "name": f"{query.upper()} manual symbol",
            "exchange": "NSE",
            "region": "NSE",
          }
        ]
      return self.send_json({"results": results})
    if parsed.path == "/api/stream":
      params = urllib.parse.parse_qs(parsed.query)
      symbols = [item for item in ((params.get("symbols") or [""])[0].split(",")) if item]
      active = ((params.get("active") or [""])[0] or "").upper() or None
      return self.stream_quotes(symbols, active)
    self.send_error(HTTPStatus.NOT_FOUND, "Not found")

  def do_POST(self) -> None:
    parsed = urllib.parse.urlparse(self.path)
    body = self.read_json()

    if parsed.path == "/api/config":
      return self.send_json(save_config(body or {}))

    if parsed.path == "/api/watchlists":
      name = (body or {}).get("name", "").strip()
      symbols = [symbol.upper() for symbol in (body or {}).get("symbols", []) if symbol]
      if not name or not symbols:
        return self.send_error(HTTPStatus.BAD_REQUEST, "name and symbols are required")
      save_watchlist(name, list(dict.fromkeys(symbols)))
      return self.send_json({"ok": True, "watchlists": list_watchlists()})

    if parsed.path == "/api/dashboard":
      symbols = [symbol.upper() for symbol in (body or {}).get("symbols", []) if symbol]
      active = ((body or {}).get("active") or "").upper() or None
      chart_range = ((body or {}).get("chartRange") or "1M").upper()
      return self.send_json(build_dashboard(symbols, active, chart_range))

    if parsed.path == "/api/lab":
      symbol = ((body or {}).get("symbol") or "").strip().upper()
      if not symbol:
        return self.send_error(HTTPStatus.BAD_REQUEST, "symbol is required")
      horizon = int((body or {}).get("horizon") or 10)
      stress = (body or {}).get("stress") or "base"
      chart_range = ((body or {}).get("chartRange") or "1M").upper()
      snapshot = build_ticker_snapshot(symbol, stress=stress, horizon=horizon, chart_range=chart_range)
      return self.send_json(
        {
          "symbol": symbol,
          "history": snapshot["history"][-40:],
          "projected": snapshot["forecast"]["projected"],
          "expectedReturn": snapshot["forecast"]["expectedReturn"],
          "direction": snapshot["forecast"]["direction"],
          "confidence": snapshot["forecast"]["confidence"],
          "triggers": snapshot["forecast"]["triggers"],
          "backtest": snapshot["lab"]["backtest"],
          "historySource": snapshot.get("historySource"),
          "historyCachedAt": snapshot.get("historyCachedAt"),
          "historyCacheState": snapshot.get("historyCacheState"),
        }
      )

    if parsed.path == "/api/research":
      query = ((body or {}).get("query") or "").strip()
      if not query:
        return self.send_error(HTTPStatus.BAD_REQUEST, "query is required")
      symbol = ((body or {}).get("symbol") or "").strip().upper() or None
      use_web = bool((body or {}).get("useWeb", True))
      use_llm = bool((body or {}).get("useLlm", True))
      return self.send_json(run_research_agent(query, symbol, use_web, use_llm))

    self.send_error(HTTPStatus.NOT_FOUND, "Not found")

  def read_json(self) -> dict | None:
    length = int(self.headers.get("Content-Length", "0") or "0")
    if length <= 0:
      return None
    raw = self.rfile.read(length).decode("utf-8")
    try:
      return json.loads(raw)
    except json.JSONDecodeError:
      return None

  def serve_file(self, filename: str, content_type: str) -> None:
    path = BASE_DIR / filename
    if not path.exists():
      self.send_error(HTTPStatus.NOT_FOUND, "File not found")
      return
    data = path.read_bytes()
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-Type", content_type)
    self.send_header("Content-Length", str(len(data)))
    self.end_headers()
    self.wfile.write(data)

  def send_json(self, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Cache-Control", "no-store")
    self.send_header("Content-Length", str(len(data)))
    self.end_headers()
    self.wfile.write(data)

  def stream_quotes(self, symbols: list[str], active: str | None) -> None:
    self.send_response(HTTPStatus.OK)
    self.send_header("Content-Type", "text/event-stream")
    self.send_header("Cache-Control", "no-cache")
    self.send_header("Connection", "keep-alive")
    self.end_headers()

    try:
      for _ in range(120):
        payload = build_live_quotes(symbols, active)
        message = f"event: quote\ndata: {json.dumps(payload)}\n\n".encode("utf-8")
        self.wfile.write(message)
        self.wfile.flush()
        time.sleep(0.8)
    except (BrokenPipeError, ConnectionResetError):
      return

  def log_message(self, format: str, *args) -> None:
    return


def run(port: int = 8000) -> None:
  init_db()
  server = ThreadingHTTPServer(("127.0.0.1", port), FinancialBoardHandler)
  print(f"Financial Board running on http://127.0.0.1:{port}")
  server.serve_forever()


if __name__ == "__main__":
  run()
