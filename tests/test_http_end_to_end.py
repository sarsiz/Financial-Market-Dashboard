import json
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from unittest import mock

import server


class HttpRouteTests(unittest.TestCase):
  def setUp(self):
    self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.FinancialBoardHandler)
    self.port = self.httpd.server_address[1]
    self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
    self.thread.start()

  def tearDown(self):
    self.httpd.shutdown()
    self.httpd.server_close()
    self.thread.join(timeout=2)

  def url(self, path: str) -> str:
    return f"http://127.0.0.1:{self.port}{path}"

  def json_get(self, path: str) -> dict:
    with urllib.request.urlopen(self.url(path), timeout=5) as response:
      return json.loads(response.read().decode("utf-8"))

  def json_post(self, path: str, payload: dict) -> dict:
    request = urllib.request.Request(
      self.url(path),
      data=json.dumps(payload).encode("utf-8"),
      headers={"Content-Type": "application/json"},
      method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
      return json.loads(response.read().decode("utf-8"))

  def test_dashboard_and_academy_routes_return_expected_payloads(self):
    dashboard_payload = {
      "provider": "yahoo",
      "updatedAt": "2026-04-01T00:00:00+00:00",
      "watchlist": [{"symbol": "ICICIBANK.NS", "price": 100.0, "changePercent": 1.2, "currency": "INR", "exchange": "NSE", "volume": 1000}],
      "active": {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "forecast": {"direction": "Bullish", "confidence": 70, "fairValueGap": 2.1, "eventPressureLabel": "Low", "mae": 1.1, "expectedReturn": 3.2, "projected": [101, 102], "models": {"agreement": {"label": "Aligned", "score": 80, "summary": "Classic and modern overlays both lean bullish."}}}, "recommendation": {"buy": 54, "hold": 31, "sell": 15, "signal": "Buy bias"}, "history": [99, 100], "stats": [], "relationshipCards": [], "driverCards": [], "lab": {"symbol": "ICICIBANK.NS", "history": [99, 100], "projected": [101], "expectedReturn": 3.2, "direction": "Bullish", "confidence": 70, "triggers": [], "backtest": {"mae": 1.1, "medianApe": 1.0, "hitRate": 60.0, "sampleCount": 4}}, "marketSession": {"status": "Open", "nextTransitionAt": "2026-04-01T09:00:00+00:00", "transitionLabel": "close", "hoursLabel": "09:15-15:30 IST", "timezone": "Asia/Kolkata"}, "regime": "Balanced regime", "currency": "INR", "price": 100.0, "changePercent": 1.2, "volume": 1000, "exchange": "NSE", "marketState": "REGULAR", "dataSource": "Yahoo Chart", "asOf": None},
      "macroPulse": [],
      "radar": {"summary": "Radar", "headlines": [], "hotspots": [], "items": []},
      "headlines": [],
    }
    academy_payload = {
      "research": server.RESEARCH_REFERENCES,
      "classicResearch": server.CLASSIC_QUANT_REFERENCES,
      "symbol": "ICICIBANK.NS",
      "summary": "Academy summary",
      "cards": [{"title": "Classic stack read", "body": "Momentum and participation are supportive."}],
      "sources": [{"title": "Source one", "url": "https://example.com/1"}],
    }

    with mock.patch.object(server, "build_dashboard", return_value=dashboard_payload), mock.patch.object(
      server, "build_academy_payload", return_value=academy_payload
    ):
      dashboard = self.json_post("/api/dashboard", {"symbols": ["ICICIBANK.NS"], "active": "ICICIBANK.NS", "chartRange": "1M"})
      academy = self.json_get("/api/academy?symbol=ICICIBANK.NS")

    self.assertEqual(dashboard["active"]["symbol"], "ICICIBANK.NS")
    self.assertEqual(dashboard["active"]["forecast"]["models"]["agreement"]["label"], "Aligned")
    self.assertEqual(academy["symbol"], "ICICIBANK.NS")
    self.assertEqual(academy["sources"][0]["url"], "https://example.com/1")


if __name__ == "__main__":
  unittest.main()
