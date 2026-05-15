#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


BASE_URL = os.environ.get("FINANCIAL_BOARD_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def request_json(path: str, method: str = "GET", payload: dict | None = None) -> tuple[int, dict]:
  data = None
  headers = {"Accept": "application/json"}
  if payload is not None:
    data = json.dumps(payload).encode("utf-8")
    headers["Content-Type"] = "application/json"
  request = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
  with urllib.request.urlopen(request, timeout=30) as response:
    return response.status, json.loads(response.read().decode("utf-8"))


def assert_ok(name: str, condition: bool, details: str = "") -> None:
  if not condition:
    raise AssertionError(f"{name} failed{f': {details}' if details else ''}")
  print(f"[ok] {name}")


def main() -> int:
  status, health = request_json("/api/health")
  assert_ok("health endpoint", status == 200 and health.get("status") == "ok", str(health))

  status, config = request_json("/api/config")
  assert_ok("config endpoint", status == 200 and "provider" in config, str(config))

  dashboard_payload = {
    "symbols": ["BHARTIARTL.NS", "ICICIBANK.NS", "GLENMARK.NS"],
    "active": "ICICIBANK.NS",
    "chartRange": "1M",
    "region": "india",
  }
  status, dashboard = request_json("/api/dashboard", method="POST", payload=dashboard_payload)
  assert_ok("dashboard endpoint", status == 200 and dashboard.get("active", {}).get("symbol") == "ICICIBANK.NS")
  assert_ok("global markets payload", len(dashboard.get("globalMarkets") or []) >= 6)
  assert_ok("region payload", dashboard.get("selectedRegion") == "india")

  query = "symbols=BHARTIARTL.NS,ICICIBANK.NS,GLENMARK.NS&active=ICICIBANK.NS&region=india"
  status, overview = request_json(f"/api/overview?{query}")
  assert_ok("overview endpoint", status == 200 and overview.get("active", {}).get("symbol") == "ICICIBANK.NS")

  status, radar = request_json("/api/radar?symbol=ICICIBANK.NS")
  assert_ok("radar endpoint", status == 200 and "radar" in radar)

  status, events = request_json("/api/events?category=business&symbol=ICICIBANK.NS")
  assert_ok("events endpoint", status == 200 and isinstance(events.get("items"), list))

  print("\nSmoke test completed successfully.")
  return 0


if __name__ == "__main__":
  try:
    raise SystemExit(main())
  except urllib.error.URLError as error:
    print(f"Smoke test failed: {error}", file=sys.stderr)
    raise SystemExit(1)
  except AssertionError as error:
    print(str(error), file=sys.stderr)
    raise SystemExit(1)
