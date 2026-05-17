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

  def test_vendor_graph_asset_is_served(self):
    with urllib.request.urlopen(self.url("/vendor/cytoscape.min.js"), timeout=5) as response:
      body = response.read(80).decode("utf-8", errors="ignore")

    self.assertEqual(response.status, 200)
    self.assertIn("javascript", response.headers.get("Content-Type", ""))
    self.assertTrue(body)

  def test_dashboard_and_academy_routes_return_expected_payloads(self):
    dashboard_payload = {
      "provider": "yahoo",
      "updatedAt": "2026-04-01T00:00:00+00:00",
      "selectedRegion": "india",
      "regionOptions": [{"key": "us", "label": "United States"}, {"key": "india", "label": "India"}],
      "watchlist": [{"symbol": "ICICIBANK.NS", "price": 100.0, "changePercent": 1.2, "currency": "INR", "exchange": "NSE", "volume": 1000}],
      "active": {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "forecast": {"direction": "Bullish", "confidence": 70, "fairValueGap": 2.1, "eventPressureLabel": "Low", "mae": 1.1, "expectedReturn": 3.2, "projected": [101, 102], "models": {"agreement": {"label": "Aligned", "score": 80, "summary": "Classic and modern overlays both lean bullish."}}}, "recommendation": {"buy": 54, "hold": 31, "sell": 15, "signal": "Buy bias"}, "history": [99, 100], "stats": [], "relationshipCards": [], "driverCards": [], "lab": {"symbol": "ICICIBANK.NS", "history": [99, 100], "projected": [101], "expectedReturn": 3.2, "direction": "Bullish", "confidence": 70, "triggers": [], "backtest": {"mae": 1.1, "medianApe": 1.0, "hitRate": 60.0, "sampleCount": 4}}, "marketSession": {"status": "Open", "nextTransitionAt": "2026-04-01T09:00:00+00:00", "transitionLabel": "close", "hoursLabel": "09:15-15:30 IST", "timezone": "Asia/Kolkata"}, "regime": "Balanced regime", "currency": "INR", "price": 100.0, "changePercent": 1.2, "volume": 1000, "exchange": "NSE", "marketState": "REGULAR", "dataSource": "Yahoo Chart", "asOf": None},
      "macroPulse": [],
      "radar": {"summary": "Radar", "headlines": [], "hotspots": [], "items": []},
      "headlines": [],
      "regions": {"us": {"region": "us"}, "india": {"region": "india"}},
      "comparison": {"rows": [], "summary": "Comparison"},
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
    self.assertEqual(dashboard["selectedRegion"], "india")
    self.assertEqual(dashboard["active"]["forecast"]["models"]["agreement"]["label"], "Aligned")
    self.assertEqual(academy["symbol"], "ICICIBANK.NS")
    self.assertEqual(academy["sources"][0]["url"], "https://example.com/1")

  def test_events_route_returns_timestamped_items(self):
    event_payload = {
      "category": "world",
      "query": "latest world news",
      "brief": "World headlines remain market-relevant.",
      "asOf": "2026-04-02T00:00:00+00:00",
      "items": [
        {
          "title": "Major macro event",
          "url": "https://example.com/world",
          "source": "example.com",
          "category": "world",
          "publishedAt": "2026-04-02T01:00:00+00:00",
          "significance": 7,
        }
      ],
    }

    with mock.patch.object(server, "build_event_feed", return_value=event_payload):
      events = self.json_get("/api/events?category=world&symbol=ICICIBANK.NS")

    self.assertEqual(events["category"], "world")
    self.assertTrue(events["asOf"])
    self.assertEqual(events["items"][0]["publishedAt"], "2026-04-02T01:00:00+00:00")

  def test_radar_route_returns_radar_payload(self):
    radar_payload = {
      "updatedAt": "2026-04-02T00:00:00+00:00",
      "symbol": "ICICIBANK.NS",
      "radar": {"summary": "Radar summary", "headlines": ["Headline one"], "hotspots": [], "items": []},
      "headlines": ["Headline one"],
    }

    with mock.patch.object(server, "build_radar_payload", return_value=radar_payload):
      radar = self.json_get("/api/radar?symbol=ICICIBANK.NS")

    self.assertEqual(radar["symbol"], "ICICIBANK.NS")
    self.assertEqual(radar["radar"]["summary"], "Radar summary")

  def test_overview_route_returns_fast_payload(self):
    overview_payload = {
      "updatedAt": "2026-04-02T00:00:00+00:00",
      "selectedRegion": "us",
      "watchlist": [{"symbol": "AAPL", "price": 210.12, "changePercent": 0.5, "currency": "USD", "exchange": "NASDAQ", "volume": 1000}],
      "active": {
        "symbol": "AAPL",
        "name": "Apple",
        "price": 210.12,
        "changePercent": 0.5,
        "currency": "USD",
        "exchange": "NASDAQ",
        "marketState": "REGULAR",
        "marketSession": {"status": "Open", "transitionLabel": "close", "timezone": "America/New_York"},
        "regime": "Refreshing active view",
      },
    }

    with mock.patch.object(server, "build_overview_payload", return_value=overview_payload):
      overview = self.json_get("/api/overview?symbols=AAPL&active=AAPL")

    self.assertEqual(overview["active"]["symbol"], "AAPL")
    self.assertEqual(overview["active"]["marketSession"]["timezone"], "America/New_York")

  def test_quotes_route_returns_lean_payload_and_passes_symbols(self):
    quotes_payload = {
      "updatedAt": "2026-04-02T00:00:00+00:00",
      "watchlist": [{"symbol": "AAPL", "price": 210.12, "previousClose": 209.0, "changePercent": 0.53, "currency": "USD", "exchange": "NASDAQ", "marketState": "REGULAR", "dataSource": "Yahoo Chart", "asOf": "2026-04-02T00:00:00+00:00", "receivedAt": "2026-04-02T00:00:00+00:00", "volume": 1000, "name": "Apple"}],
      "active": {"symbol": "AAPL", "price": 210.12, "changePercent": 0.53, "currency": "USD"},
      "mode": "quotes",
    }

    with mock.patch.object(server, "build_quote_snapshot", return_value=quotes_payload) as snap_mock:
      payload = self.json_get("/api/quotes?symbols=AAPL,MSFT&active=AAPL")

    self.assertEqual(payload["mode"], "quotes")
    self.assertEqual(payload["watchlist"][0]["symbol"], "AAPL")
    self.assertEqual(payload["active"]["symbol"], "AAPL")
    # The route should pass uppercased, comma-split symbols straight through.
    snap_mock.assert_called_once_with(["AAPL", "MSFT"], "AAPL")
    # The lean payload must not include heavier overview fields (regime, marketSession, region).
    self.assertNotIn("selectedRegion", payload)
    self.assertNotIn("regime", payload["active"])

  def test_quotes_route_reuses_cached_payload_within_ttl(self):
    call_count = {"value": 0}

    def fake_builder(symbols, active):
      call_count["value"] += 1
      return {
        "updatedAt": "2026-04-02T00:00:00+00:00",
        "watchlist": [{"symbol": "AAPL", "price": 210.12, "previousClose": 209.0, "changePercent": 0.53}],
        "active": {"symbol": "AAPL", "price": 210.12, "changePercent": 0.53},
        "mode": "quotes",
        "_callIndex": call_count["value"],
      }

    # build_quote_snapshot wraps the lean payload in memory_cached_value with
    # QUOTES_PAYLOAD_CACHE_TTL. Two consecutive calls with the same symbols
    # within TTL should be served from cache (the inner builder is invoked once).
    server._memory_payload_cache.clear()  # ensure clean cache for the test
    with mock.patch.object(server, "fetch_live_quotes", side_effect=lambda symbols, fast=False: {
        "AAPL": {
          "regularMarketPrice": 210.12,
          "regularMarketPreviousClose": 209.0,
          "regularMarketChangePercent": 0.53,
          "regularMarketVolume": 1000,
          "currency": "USD",
          "exchange": "NASDAQ",
          "fullExchangeName": "NASDAQ",
          "shortName": "Apple",
          "quoteSource": "Yahoo Chart",
        },
      }):
      first = self.json_get("/api/quotes?symbols=AAPL&active=AAPL")
      second = self.json_get("/api/quotes?symbols=AAPL&active=AAPL")

    # updatedAt is generated inside the builder, so equality across two calls
    # is the strongest signal that the cache is being shared.
    self.assertEqual(first.get("updatedAt"), second.get("updatedAt"))
    self.assertEqual(first["watchlist"][0]["symbol"], "AAPL")


if __name__ == "__main__":
  unittest.main()
