from __future__ import annotations

import csv
import json
import socket
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MACRO_DIR = DATA_DIR / "macro"
US_DIR = MACRO_DIR / "us"
INDIA_DIR = MACRO_DIR / "india"

FRED_SERIES = {
  "DGS2": {"label": "US 2Y Treasury", "domain": "rates"},
  "DGS5": {"label": "US 5Y Treasury", "domain": "rates"},
  "DGS10": {"label": "US 10Y Treasury", "domain": "rates"},
  "DGS30": {"label": "US 30Y Treasury", "domain": "rates"},
  "T10YIE": {"label": "US 10Y Breakeven Inflation", "domain": "inflation"},
  "FEDFUNDS": {"label": "Fed Funds Effective Rate", "domain": "policy"},
  "CPIAUCSL": {"label": "US CPI", "domain": "inflation"},
  "SP500": {"label": "S&P 500", "domain": "equities"},
  "UNRATE": {"label": "US Unemployment Rate", "domain": "labor"},
}


def ensure_dirs() -> None:
  (US_DIR / "series").mkdir(parents=True, exist_ok=True)
  (INDIA_DIR / "series").mkdir(parents=True, exist_ok=True)


def fetch_csv(url: str) -> str:
  request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
  with urllib.request.urlopen(request, timeout=12) as response:
    return response.read().decode("utf-8")


def download_fred_series(series_id: str) -> dict:
  url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
  text = fetch_csv(url)
  reader = csv.DictReader(text.splitlines())
  points = []
  for row in reader:
    date = row.get("DATE")
    value = row.get(series_id)
    if not date or value in {None, ".", ""}:
      continue
    try:
      numeric = float(value)
    except ValueError:
      continue
    points.append({"date": date, "value": numeric})
  meta = FRED_SERIES[series_id]
  payload = {
    "seriesId": series_id,
    "label": meta["label"],
    "domain": meta["domain"],
    "source": "FRED",
    "sourceUrl": url,
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "points": points,
  }
  (US_DIR / "series" / f"{series_id}.json").write_text(json.dumps(payload, indent=2))
  return payload


def series_stub(series_id: str, error: str) -> dict:
  meta = FRED_SERIES[series_id]
  payload = {
    "seriesId": series_id,
    "label": meta["label"],
    "domain": meta["domain"],
    "source": "FRED",
    "sourceUrl": f"https://fred.stlouisfed.org/series/{series_id}",
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "points": [],
    "status": "fetch_error",
    "error": error,
  }
  (US_DIR / "series" / f"{series_id}.json").write_text(json.dumps(payload, indent=2))
  return payload


def build_india_reference_payload() -> dict:
  payload = {
    "region": "india",
    "source": "Curated local reference",
    "sourceUrl": "https://www.rbi.org.in/",
    "updatedAt": datetime.now(timezone.utc).isoformat(),
    "series": [
      {
        "key": "policy_rate",
        "label": "RBI Repo Rate",
        "cadence": "event-driven",
        "status": "manual_reference",
      },
      {
        "key": "cpi",
        "label": "India CPI",
        "cadence": "monthly",
        "status": "manual_reference",
      },
      {
        "key": "10y_gsec",
        "label": "India 10Y G-Sec",
        "cadence": "daily",
        "status": "wired_via_dashboard_fallback",
      },
    ],
  }
  (INDIA_DIR / "series" / "india_reference.json").write_text(json.dumps(payload, indent=2))
  return payload


def build_manifest(us_payloads: list[dict], india_payload: dict) -> dict:
  manifest = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "regions": {
      "us": {
        "seriesCount": len(us_payloads),
        "sources": sorted({payload["source"] for payload in us_payloads}),
        "series": [
          {
            "seriesId": payload["seriesId"],
            "label": payload["label"],
            "domain": payload["domain"],
            "points": len(payload["points"]),
            "updatedAt": payload["updatedAt"],
            "path": str((US_DIR / "series" / f"{payload['seriesId']}.json").relative_to(BASE_DIR)),
          }
          for payload in us_payloads
        ],
      },
      "india": {
        "seriesCount": len(india_payload["series"]),
        "sources": [india_payload["source"]],
        "series": india_payload["series"],
      },
    },
  }
  (MACRO_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
  return manifest


def main() -> None:
  ensure_dirs()
  us_payloads = []
  for series_id in FRED_SERIES:
    try:
      us_payloads.append(download_fred_series(series_id))
    except (urllib.error.URLError, TimeoutError, socket.timeout, ValueError) as exc:
      us_payloads.append(series_stub(series_id, str(exc)))
  india_payload = build_india_reference_payload()
  manifest = build_manifest(us_payloads, india_payload)
  print(json.dumps({"usSeries": len(us_payloads), "usFetched": sum(1 for payload in us_payloads if payload.get("points")), "indiaSeries": len(india_payload["series"]), "manifest": str((MACRO_DIR / "manifest.json").relative_to(BASE_DIR))}, indent=2))


if __name__ == "__main__":
  main()
