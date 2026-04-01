import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import server


class TempDatabaseTestCase(unittest.TestCase):
  def setUp(self):
    self.tempdir = tempfile.TemporaryDirectory()
    self.db_path = Path(self.tempdir.name) / "test_financial_board.db"
    self.config_path = Path(self.tempdir.name) / "test_config.json"
    self.db_patcher = mock.patch.object(server, "DB_PATH", self.db_path)
    self.config_patcher = mock.patch.object(server, "CONFIG_PATH", self.config_path)
    self.db_patcher.start()
    self.config_patcher.start()
    server.init_db()

  def tearDown(self):
    self.db_patcher.stop()
    self.config_patcher.stop()
    self.tempdir.cleanup()


class HistoryCacheTests(TempDatabaseTestCase):
  def test_save_and_load_history_cache_round_trip(self):
    server.save_history_cache(
      "icicibank.ns",
      "1m",
      [1.25, 2.5, 3.75],
      {"exchangeName": "NSE"},
      "Yahoo Chart",
    )

    payload = server.load_cached_history("ICICIBANK.NS", "1M")

    self.assertIsNotNone(payload)
    closes, meta, source, updated_at = payload
    self.assertEqual(closes, [1.25, 2.5, 3.75])
    self.assertEqual(meta["exchangeName"], "NSE")
    self.assertEqual(source, "Yahoo Chart")
    self.assertTrue(updated_at)

  def test_build_history_prefers_fresh_cache(self):
    server.save_history_cache(
      "ICICIBANK.NS",
      "1M",
      [101.0, 102.5, 103.2],
      {"currency": "INR"},
      "Local cache",
    )

    with mock.patch.object(server, "fetch_yahoo_chart") as yahoo_mock, mock.patch.object(
      server, "fetch_google_finance_history"
    ) as google_mock:
      history, meta = server.build_history("ICICIBANK.NS", "1M")

    self.assertEqual(history, [101.0, 102.5, 103.2])
    self.assertEqual(meta["historySource"], "Local cache")
    self.assertEqual(meta["historyCacheState"], "fresh")
    yahoo_mock.assert_not_called()
    google_mock.assert_not_called()

  def test_build_history_falls_back_to_google_and_saves_cache(self):
    with mock.patch.object(server, "fetch_yahoo_chart", return_value=None), mock.patch.object(
      server,
      "fetch_google_finance_history",
      return_value=([1200.0, 1210.5, 1222.0], {"historySource": "Google Finance Page"}),
    ):
      history, meta = server.build_history("ICICIBANK.NS", "1M")

    self.assertEqual(history, [1200.0, 1210.5, 1222.0])
    self.assertEqual(meta["historySource"], "Google Finance Page")
    self.assertEqual(meta["historyCacheState"], "fresh")

    cached = server.load_cached_history("ICICIBANK.NS", "1M")
    self.assertIsNotNone(cached)
    self.assertEqual(cached[0], [1200.0, 1210.5, 1222.0])

  def test_build_history_uses_stale_cache_when_live_sources_fail(self):
    server.save_history_cache(
      "ICICIBANK.NS",
      "1M",
      [900.0, 905.0, 910.0],
      {"currency": "INR"},
      "Google Finance Page",
    )

    stale_time = (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat()
    with sqlite3.connect(self.db_path) as connection:
      connection.execute(
        "UPDATE history_cache SET updated_at = ? WHERE symbol = ? AND chart_range = ?",
        (stale_time, "ICICIBANK.NS", "1M"),
      )
      connection.commit()

    with mock.patch.object(server, "fetch_yahoo_chart", return_value=None), mock.patch.object(
      server, "fetch_google_finance_history", return_value=([], {})
    ):
      history, meta = server.build_history("ICICIBANK.NS", "1M")

    self.assertEqual(history, [900.0, 905.0, 910.0])
    self.assertEqual(meta["historySource"], "Google Finance Page")
    self.assertEqual(meta["historyCacheState"], "stale")


class ForecastAndLabTests(unittest.TestCase):
  def test_build_forecast_contains_classic_modern_agreement(self):
    history = [100 + (index * 0.7) for index in range(40)]
    quote = {"regularMarketPrice": history[-1], "regularMarketPreviousClose": history[-2], "fullExchangeName": "NSE"}

    forecast = server.build_forecast("ICICIBANK.NS", quote, {}, history, horizon=10, news_count=3)

    self.assertIn("models", forecast)
    self.assertIn("classic", forecast["models"])
    self.assertIn("modern", forecast["models"])
    self.assertIn("agreement", forecast["models"])
    self.assertIn("label", forecast["models"]["agreement"])

  def test_build_market_session_for_nse_closed_window(self):
    class FrozenDatetime(datetime):
      @classmethod
      def now(cls, tz=None):
        base = datetime(2026, 4, 1, 12, 0, tzinfo=timezone.utc)
        return base if tz is None else base.astimezone(tz)

    with mock.patch.object(server, "datetime", FrozenDatetime):
      session = server.build_market_session("NSE", "NSE", "CLOSED")

    self.assertEqual(session["status"], "Closed")
    self.assertEqual(session["timezone"], "Asia/Kolkata")
    self.assertEqual(session["transitionLabel"], "open")
    self.assertTrue(session["nextTransitionAt"])

  def test_build_recommendation_normalizes_to_hundred(self):
    recommendation = server.build_recommendation(
      {
        "confidence": 71,
        "expectedReturn": 4.4,
        "fairValueGap": 3.0,
        "eventPressure": 0.18,
      }
    )

    self.assertEqual(
      recommendation["buy"] + recommendation["hold"] + recommendation["sell"],
      100,
    )
    self.assertEqual(recommendation["signal"], "Buy bias")

  def test_build_backtest_produces_samples_with_short_real_history(self):
    history = [100 + index for index in range(20)]
    quote = {"regularMarketPrice": history[-1], "regularMarketPreviousClose": history[-2]}

    def fake_forecast(symbol, quote, summary, window, stress="base", horizon=5, news_count=0):
      current = window[-1]
      return {"projected": [current + 1 for _ in range(horizon)]}

    with mock.patch.object(server, "build_forecast", side_effect=fake_forecast):
      backtest = server.build_backtest("AAPL", history, quote, {}, horizon=5, stress="base", news_count=0)

    self.assertGreater(backtest["sampleCount"], 0)
    self.assertGreaterEqual(backtest["hitRate"], 0.0)

  def test_build_academy_payload_contains_summary_cards_and_sources(self):
    snapshot = {
      "symbol": "ICICIBANK.NS",
      "name": "ICICI Bank",
      "exchange": "NSE",
      "forecast": {
        "direction": "Bullish",
        "models": {
          "modern": {"summary": "Modern overlay is constructive."},
          "agreement": {"summary": "Classic and modern overlays both lean bullish.", "score": 82},
        },
      },
      "classicQuant": {"summary": "Classic stack is anchored on momentum and participation."},
      "headlines": ["ICICI Bank expands partnership flow"],
    }
    with mock.patch.object(server, "build_ticker_snapshot", return_value=snapshot), mock.patch.object(
      server,
      "duckduckgo_search",
      return_value=[{"title": "ICICI Bank latest update", "url": "https://example.com/icici"}],
    ), mock.patch.object(server, "generate_local_llm_answer", return_value=None):
      payload = server.build_academy_payload("ICICIBANK.NS")

    self.assertEqual(payload["symbol"], "ICICIBANK.NS")
    self.assertTrue(payload["summary"])
    self.assertGreaterEqual(len(payload["cards"]), 3)
    self.assertEqual(payload["sources"][0]["url"], "https://example.com/icici")


class DashboardAssemblyTests(unittest.TestCase):
  def test_build_dashboard_returns_expected_shape(self):
    snapshot = {
      "symbol": "ICICIBANK.NS",
      "name": "ICICI Bank",
      "history": [100.0, 101.0, 102.0],
      "historySource": "Google Finance Page",
      "forecast": {
        "projected": [103.0, 104.0],
        "expectedReturn": 2.5,
        "direction": "Buy bias",
        "confidence": 66.0,
      },
      "lab": {
        "symbol": "ICICIBANK.NS",
        "history": [100.0, 101.0, 102.0],
        "projected": [103.0, 104.0],
        "expectedReturn": 2.5,
        "direction": "Buy bias",
        "confidence": 66.0,
        "triggers": [],
        "backtest": {"mae": 1.2, "medianApe": 1.0, "hitRate": 60.0, "sampleCount": 4},
        "historySource": "Google Finance Page",
      },
      "driverCards": [],
      "relationshipCards": [],
      "stats": [],
      "headlines": ["Headline 1"],
      "price": 102.0,
      "previousClose": 100.0,
      "changePercent": 2.0,
      "volume": 1234,
      "currency": "INR",
      "exchange": "NSE",
      "region": "NSE",
      "marketState": "REGULAR",
      "dataSource": "Google Finance",
      "asOf": None,
      "sector": "Financial Services",
      "industry": "Banks",
      "regime": "Balanced regime",
      "recommendation": {"buy": 52, "hold": 33, "sell": 15, "signal": "Buy bias"},
      "chartRange": "1M",
      "sentiment": {"label": "Neutral", "score": 0.0},
    }

    with mock.patch.object(
      server,
      "fetch_live_quotes",
      return_value={
        "BHARTIARTL.NS": {
          "shortName": "Bharti Airtel",
          "regularMarketPrice": 1200.0,
          "regularMarketPreviousClose": 1190.0,
          "regularMarketChangePercent": 0.84,
          "regularMarketVolume": 10000,
          "currency": "INR",
          "exchange": "NSE",
          "fullExchangeName": "NSE",
          "quoteSource": "Google Finance",
        },
        "ICICIBANK.NS": {
          "shortName": "ICICI Bank",
          "regularMarketPrice": 102.0,
          "regularMarketPreviousClose": 100.0,
          "regularMarketChangePercent": 2.0,
          "regularMarketVolume": 1234,
          "currency": "INR",
          "exchange": "NSE",
          "fullExchangeName": "NSE",
          "quoteSource": "Google Finance",
        },
      },
    ), mock.patch.object(server, "build_ticker_snapshot", return_value=snapshot), mock.patch.object(
      server, "build_macro_pulse", return_value=[{"label": "NIFTY 50", "value": "22000", "trend": "+0.5%", "positive": True}]
    ), mock.patch.object(
      server,
      "build_market_radar",
      return_value={"summary": "Radar summary", "headlines": ["Headline 1"], "hotspots": [], "items": []},
    ), mock.patch.object(server, "load_config", return_value={"provider": "yahoo"}):
      payload = server.build_dashboard(["BHARTIARTL.NS"], "ICICIBANK.NS", "1M")

    self.assertEqual(payload["provider"], "yahoo")
    self.assertEqual(payload["active"]["symbol"], "ICICIBANK.NS")
    self.assertEqual(payload["watchlist"][0]["symbol"], "ICICIBANK.NS")
    self.assertEqual(payload["watchlist"][1]["symbol"], "BHARTIARTL.NS")
    self.assertEqual(payload["macroPulse"][0]["label"], "NIFTY 50")
    self.assertEqual(payload["radar"]["summary"], "Radar summary")


if __name__ == "__main__":
  unittest.main()
