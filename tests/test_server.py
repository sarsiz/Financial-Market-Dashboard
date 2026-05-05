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
    server.HISTORY_WARMUP_JOBS.clear()
    server.HISTORY_INFLIGHT.clear()
    server._sector_cache.clear()
    server.init_db()

  def tearDown(self):
    self.db_patcher.stop()
    self.config_patcher.stop()
    self.tempdir.cleanup()


class HistoryCacheTests(TempDatabaseTestCase):
  def test_save_config_pins_local_llm_model_to_bonsai_1bit(self):
    saved = server.save_config(
      {
        "provider": "yahoo",
        "alphaVantageApiKey": "",
        "localLlmBaseUrl": "http://127.0.0.1:11434",
        "localLlmModel": "some-other-model",
      }
    )

    self.assertEqual(saved["localLlmModel"], "Bonsai-8B-1bit")
    loaded = server.load_config()
    self.assertEqual(loaded["localLlmModel"], "Bonsai-8B-1bit")

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

  def test_build_history_can_fall_back_to_stooq_for_us_symbols(self):
    with mock.patch.object(server, "fetch_yahoo_chart", return_value=None), mock.patch.object(
      server, "fetch_google_finance_history", return_value=([], {})
    ), mock.patch.object(server, "fetch_stooq_history", return_value=([201.0, 202.4, 204.1], {"historySource": "Stooq CSV"})):
      history, meta = server.build_history("AAPL", "1M")

    self.assertEqual(history, [201.0, 202.4, 204.1])
    self.assertEqual(meta["historySource"], "Stooq CSV")

  def test_build_history_can_map_bse_symbol_to_nse_candidate(self):
    with mock.patch.object(server, "fetch_yahoo_chart", side_effect=[None, {"meta": {}, "timestamp": [1, 2], "indicators": {"quote": [{"close": [100.0, 101.5]}]}}]), mock.patch.object(
      server, "fetch_google_finance_history", return_value=([], {})
    ):
      history, meta = server.build_history("ICICIBANK.BO", "1M")

    self.assertEqual(history, [100.0, 101.5])
    self.assertEqual(meta["historyMappedSymbol"], "ICICIBANK.NS")

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

  def test_save_and_load_generic_payload_cache_round_trip(self):
    server.save_payload_cache("region_events::us", {"items": [{"title": "Fed event"}], "source": "RSS"}, "RSS")

    payload = server.load_cached_payload("region_events::us")

    self.assertIsNotNone(payload)
    cached_payload, source, updated_at = payload
    self.assertEqual(cached_payload["items"][0]["title"], "Fed event")
    self.assertEqual(source, "RSS")
    self.assertTrue(updated_at)

  def test_allowed_outbound_url_blocks_unknown_and_http_hosts(self):
    self.assertTrue(server.is_allowed_outbound_url("https://query1.finance.yahoo.com/v7/finance/quote"))
    self.assertFalse(server.is_allowed_outbound_url("http://query1.finance.yahoo.com/v7/finance/quote"))
    self.assertFalse(server.is_allowed_outbound_url("https://example.com/data.json"))

  def test_google_finance_quote_parser_reads_deep_quote_header(self):
    html = """
      <main>
        <div>BHARTIARTL</div><div>Research</div><div>BHARTIARTL:NSE</div>
        <div>check_indeterminate_small</div><div>Add to list</div>
        <div>Bharti Airtel Ltd</div><div>&#8377;1,829.90</div>
        <div>arrow_downward</div><div>-3.02%</div><div>(</div><div>-56.90</div><div>) Today</div>
        <div>May 4, 2:55:25 PM GMT+5:30 &middot; INR</div>
        <div>Open</div><div>&#8377;1,873.20</div>
        <div>High</div><div>&#8377;1,895.30</div>
        <div>Low</div><div>&#8377;1,824.20</div>
        <div>Mkt. cap</div><div>11.14T</div>
        <div>Avg. vol.</div><div>8.41M</div>
        <div>Volume</div><div>9.05M</div>
        <div>P/E ratio</div><div>36.17</div>
        <div>52-wk high</div><div>&#8377;2,174.50</div>
        <div>52-wk low</div><div>&#8377;1,746.90</div>
      </main>
    """
    with mock.patch.object(server, "text_get", return_value=html):
      quote = server.fetch_google_finance_quote("BHARTIARTL.NS", "NSE")

    self.assertEqual(quote["regularMarketPrice"], 1829.90)
    self.assertAlmostEqual(quote["regularMarketPreviousClose"], 1886.8)
    self.assertEqual(quote["regularMarketChangePercent"], -3.02)
    self.assertEqual(quote["regularMarketVolume"], 9050000)
    self.assertEqual(quote["averageDailyVolume3Month"], 8410000)
    self.assertEqual(quote["quoteSource"], "Google Finance")
    self.assertIsInstance(quote["regularMarketTime"], int)

  def test_quote_freshness_flags_history_during_open_market(self):
    as_of = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    freshness = server.quote_freshness(as_of, {"isOpen": True}, "History-derived")

    self.assertEqual(freshness["label"], "Historical fallback")
    self.assertEqual(freshness["state"], "stale")
    self.assertTrue(freshness["isStale"])
    self.assertIn("not a confirmed live quote", freshness["note"])

  def test_google_finance_history_timestamps_use_exchange_timezone(self):
    timestamp = server.timestamp_from_google_block([2026, 5, 4, 14, 55], "Asia/Kolkata")

    self.assertEqual(timestamp, "2026-05-04T09:25:00+00:00")

  def test_get_or_refresh_cached_payload_prefers_fresh_cache(self):
    server.save_payload_cache("region_calendar::india", {"items": [{"title": "RBI event"}], "source": "RBI"}, "RBI")

    with mock.patch.object(server, "fetch_rbi_calendar_items") as rbi_mock:
      payload = server.build_region_calendar("india")

    self.assertEqual(payload["items"][0]["title"], "RBI event")
    self.assertEqual(payload["cacheState"], "fresh")
    rbi_mock.assert_not_called()

  def test_get_or_refresh_cached_payload_uses_stale_cache_when_builder_fails(self):
    server.save_payload_cache("region_events::us", {"items": [{"title": "Old Fed event"}], "source": "RSS"}, "RSS")
    stale_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    with sqlite3.connect(self.db_path) as connection:
      connection.execute(
        "UPDATE payload_cache SET updated_at = ? WHERE cache_key = ?",
        (stale_time, "region_events::us"),
      )
      connection.commit()

    with mock.patch.object(server, "build_event_feed", side_effect=RuntimeError("boom")):
      payload = server.build_region_event_context("us")

    self.assertEqual(payload["items"][0]["title"], "Old Fed event")
    self.assertEqual(payload["cacheState"], "stale")

  def test_save_and_load_historical_records_round_trip(self):
    server.save_historical_records(
      "AAPL",
      "1d",
      [
        {"timestamp": "2026-04-01T00:00:00+00:00", "value": 201.1, "volume": 1000},
        {"timestamp": "2026-04-02T00:00:00+00:00", "value": 203.4, "volume": 1200},
      ],
      "Yahoo Chart",
    )

    rows = server.load_historical_records("AAPL", "1d")

    self.assertEqual(len(rows), 2)
    self.assertEqual(rows[0]["value"], 201.1)
    self.assertEqual(rows[1]["volume"], 1200.0)

  def test_build_history_does_not_treat_old_records_as_fresh_quote_edge(self):
    old_timestamp = (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
    fresh_timestamp = int(datetime.now(timezone.utc).timestamp())
    server.save_historical_records(
      "ICICIBANK.NS",
      "1d",
      [
        {"timestamp": (datetime.now(timezone.utc) - timedelta(days=21)).isoformat(), "value": 1281.3},
        {"timestamp": old_timestamp, "value": 1321.9},
      ],
      "Historical records",
    )

    chart = {
      "meta": {"currency": "INR", "regularMarketPrice": 1263.4},
      "timestamp": [fresh_timestamp - 86400, fresh_timestamp],
      "indicators": {"quote": [{"close": [1281.0, 1263.4]}]},
    }
    with mock.patch.object(server, "fetch_yahoo_chart", return_value=chart), mock.patch.object(
      server, "fetch_google_finance_history", return_value=([], {})
    ):
      history, meta = server.build_history("ICICIBANK.NS", "1M")

    self.assertEqual(history[-1], 1263.4)
    self.assertEqual(meta["historySource"], "Yahoo Chart")
    self.assertNotEqual(history[-1], 1321.9)

  def test_start_history_warmup_queues_background_cache_job_once(self):
    captured = {}

    class InlineThread:
      def __init__(self, target, args, daemon=False):
        captured["target"] = target
        captured["args"] = args
        captured["daemon"] = daemon

      def start(self):
        captured["started"] = True

    with mock.patch.object(server.threading, "Thread", InlineThread):
      first = server.start_history_warmup(["ICICIBANK.NS"], ["1D", "5D"], reason="unit")
      second = server.start_history_warmup(["ICICIBANK.NS"], ["1D", "5D"], reason="unit")

    self.assertEqual(first["status"], "queued")
    self.assertEqual(second["status"], "queued")
    self.assertTrue(captured["started"])
    self.assertTrue(captured["daemon"])
    self.assertEqual(first["jobKey"], second["jobKey"])
    self.assertEqual(first["jobKey"], server.history_warmup_status()["jobs"][-1]["jobKey"])

  def test_build_sector_matrix_returns_benchmark_metadata_and_relative_returns(self):
    changes = {
      "^NSEI": (2.0, 102.0, "Unit"),
      "^NSEBANK": (3.0, 206.0, "Unit"),
      "^CNXIT": (1.0, 303.0, "Unit"),
    }
    with mock.patch.object(server, "SECTOR_INDICES", {"india": server.SECTOR_INDICES["india"][:2]}), mock.patch.object(
      server, "fetch_period_change", side_effect=lambda symbol, period: changes[symbol]
    ):
      payload = server.build_sector_matrix("india", "5D", "^NSEI")

    self.assertEqual(payload["benchmark"]["symbol"], "^NSEI")
    self.assertEqual(payload["period"], "5D")
    self.assertEqual(payload["periodLabel"], "5 days")
    self.assertIn("cacheState", payload)
    self.assertEqual(payload["sectors"][0]["relativePct"], 1.0)

  def test_run_history_warmup_skips_fresh_ranges_and_fetches_missing_ranges(self):
    job_key = server.history_warmup_key(["ICICIBANK.NS"], ["1D", "5D"])
    server.HISTORY_WARMUP_JOBS[job_key] = {"status": "queued", "jobKey": job_key}
    calls = []

    def fake_is_fresh(symbol, chart_range):
      return chart_range == "1D"

    def fake_build_history(symbol, chart_range, allow_live_refresh=True):
      calls.append((symbol, chart_range, allow_live_refresh))
      return [1.0, 2.0], {"historySource": "Unit"}

    with mock.patch.object(server, "history_cache_is_fresh", side_effect=fake_is_fresh), mock.patch.object(
      server, "build_history", side_effect=fake_build_history
    ):
      server.run_history_warmup(job_key, ["ICICIBANK.NS"], ["1D", "5D"])

    self.assertEqual(calls, [("ICICIBANK.NS", "5D", True)])
    self.assertEqual(server.HISTORY_WARMUP_JOBS[job_key]["status"], "done")
    self.assertEqual(server.HISTORY_WARMUP_JOBS[job_key]["completed"], 2)

  def test_save_and_load_derived_insight_round_trip(self):
    payload = {"state": "5D above 25D", "sma5": 105.0, "sma25": 100.0}

    server.save_derived_insight("AAPL", "1d", "sma_5_25", payload, "Unit test")
    loaded = server.load_derived_insight("AAPL", "1d", "sma_5_25")

    self.assertIsNotNone(loaded)
    self.assertEqual(loaded["state"], "5D above 25D")
    self.assertEqual(loaded["source"], "Unit test")

  def test_build_moving_average_insight_persists_signal(self):
    history = [100 + index for index in range(30)]

    signal = server.build_moving_average_insight("AAPL", history)
    loaded = server.load_derived_insight("AAPL", "1d", "sma_5_25")

    self.assertEqual(signal["nextRunBias"], "Continuation")
    self.assertIsNotNone(loaded)
    self.assertEqual(loaded["nextRunBias"], "Continuation")

  def test_relation_links_for_watchlist_prefers_precomputed_graph(self):
    relations_dir = Path(self.tempdir.name) / "relations"
    relations_dir.mkdir(parents=True, exist_ok=True)
    with mock.patch.object(server, "RELATIONS_DIR", relations_dir):
      (relations_dir / "sp500.json").write_text(
        json.dumps(
          {
            "universe": "sp500",
            "generatedAt": "2026-04-11T00:00:00+00:00",
            "source": "Precomputed relation graph",
            "links": [
              {"source": "AAPL", "target": "MSFT", "value": 0.74, "direction": "positive"},
              {"source": "AAPL", "target": "JPM", "value": 0.18, "direction": "positive"},
            ],
          }
        )
      )

      links, meta = server.relation_links_for_watchlist(
        "us",
        [
          {"symbol": "AAPL"},
          {"symbol": "MSFT"},
        ],
      )

    self.assertEqual(len(links), 1)
    self.assertEqual(links[0]["source"], "AAPL")
    self.assertEqual(meta["universe"], "sp500")

  def test_load_market_map_note_reads_local_vault_note(self):
    vault_dir = Path(self.tempdir.name) / "vault" / "market-map" / "companies"
    vault_dir.mkdir(parents=True, exist_ok=True)
    note_path = vault_dir / "AAPL.md"
    note_path.write_text(
      """---
symbol: AAPL
---

# AAPL

Apple sits inside the local market map as a duration-sensitive mega-cap.
"""
    )
    with mock.patch.object(server, "VAULT_DIR", Path(self.tempdir.name) / "vault" / "market-map"):
      note = server.load_market_map_note("AAPL")

    self.assertEqual(note["title"], "AAPL")
    self.assertIn("duration-sensitive", note["summary"])


class ForecastAndLabTests(unittest.TestCase):
  def test_calc_rsi_uses_wilder_smoothing(self):
    prices = [44.0, 44.15, 43.9, 44.35, 44.6, 44.4, 44.75, 45.0, 44.8, 45.2, 45.35, 45.1, 45.5, 45.8, 45.6, 45.9, 46.2]

    self.assertAlmostEqual(server.calc_rsi(prices, 14), 75.40, places=2)

  def test_calc_macd_keeps_emas_aligned(self):
    prices = [100 + index for index in range(40)]
    macd = server.calc_macd(prices)
    fast = server.calc_ema(prices, 12)
    slow = server.calc_ema(prices, 26)
    aligned = [f - s for f, s in zip(fast, slow)][25:]

    self.assertAlmostEqual(macd["line"], round(aligned[-1], 6), places=6)

  def test_build_forecast_contains_classic_modern_agreement(self):
    history = [100 + (index * 0.7) for index in range(40)]
    quote = {"regularMarketPrice": history[-1], "regularMarketPreviousClose": history[-2], "fullExchangeName": "NSE"}

    forecast = server.build_forecast("ICICIBANK.NS", quote, {}, history, horizon=10, news_count=3)

    self.assertIn("models", forecast)
    self.assertIn("classic", forecast["models"])
    self.assertIn("modern", forecast["models"])
    self.assertIn("agreement", forecast["models"])
    self.assertIn("label", forecast["models"]["agreement"])
    self.assertIn("rsi", forecast["factorsRaw"])
    self.assertIn("macdLine", forecast["factorsRaw"])
    self.assertTrue(all("tag" in trigger and "weight" in trigger for trigger in forecast["triggers"]))

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
    self.assertIn(recommendation["signal"], {"Buy bias", "Hold bias"})

  def test_build_recommendation_neutral_prefers_hold(self):
    recommendation = server.build_recommendation(
      {
        "confidence": 70,
        "expectedReturn": 0.0,
        "fairValueGap": 0.0,
        "eventPressure": 0.1,
      }
    )

    self.assertEqual(recommendation["buy"] + recommendation["hold"] + recommendation["sell"], 100)
    self.assertGreater(recommendation["hold"], recommendation["buy"])
    self.assertGreater(recommendation["hold"], recommendation["sell"])

  def test_build_recommendation_strong_directional_cases_balance(self):
    bullish = server.build_recommendation({"confidence": 82, "expectedReturn": 9.0, "fairValueGap": 6.0, "eventPressure": 0.05})
    bearish = server.build_recommendation({"confidence": 82, "expectedReturn": -9.0, "fairValueGap": -6.0, "eventPressure": 0.25})

    self.assertGreater(bullish["buy"], bullish["sell"])
    self.assertGreater(bearish["sell"], bearish["buy"])

  def test_local_search_finds_sector_keyword_matches(self):
    results = server.local_search_results("Pharma")

    self.assertTrue(any(item["symbol"] == "GLENMARK.NS" for item in results))
    self.assertTrue(all("matchType" in item and "score" in item for item in results))

  def test_build_decision_cockpit_returns_fact_based_scenarios(self):
    snapshot = {
      "symbol": "ICICIBANK.NS",
      "changePercent": 1.4,
      "volume": 1200000,
      "sentiment": 0.1,
      "forecast": {
        "confidence": 72,
        "expectedReturn": 3.1,
        "eventPressure": 0.22,
        "mae": 2.4,
        "movingAverageSignal": {"state": "5D above 25D", "spreadPercent": 2.2, "why": "Short trend leads."},
      },
      "recommendation": {"buy": 52, "hold": 34, "sell": 14, "signal": "Buy bias"},
    }
    region = server.build_region_payload("india", [{"symbol": "ICICIBANK.NS", "exchange": "NSE", "currency": "INR"}], snapshot)
    cockpit = server.build_decision_cockpit(snapshot, region, {"sentiment": {"score": 0.2, "label": "Constructive"}, "items": [{"title": "Bank credit growth improves"}]})

    self.assertIn("stance", cockpit)
    self.assertGreaterEqual(len(cockpit["facts"]), 4)
    self.assertTrue(cockpit["monitor"])
    self.assertIn("not direct", " ".join(cockpit["interpretation"]).lower())

  def test_build_stock_dossier_returns_core_sections_and_sourced_graph(self):
    snapshot = {
      "symbol": "ICICIBANK.NS",
      "exchange": "NSE",
      "currency": "INR",
      "dataSource": "Unit test quote",
      "price": 120,
      "previousClose": 116,
      "changePercent": 3.4,
      "volume": 1000000,
      "sector": "Financial Services",
      "forecast": {"mae": 2.0},
      "recommendation": {"buy": 50, "hold": 30, "sell": 20, "signal": "Buy bias"},
    }
    quote = {
      "regularMarketOpen": 118,
      "regularMarketDayLow": 117,
      "regularMarketDayHigh": 122,
      "fiftyTwoWeekLow": 90,
      "fiftyTwoWeekHigh": 130,
      "averageDailyVolume3Month": 900000,
      "trailingPE": 18,
    }
    summary = {
      "financialData": {
        "totalRevenue": {"raw": 1000},
        "returnOnEquity": {"raw": 0.15},
        "recommendationKey": "buy",
        "numberOfAnalystOpinions": {"raw": 12},
      },
      "defaultKeyStatistics": {"trailingEps": {"raw": 10}},
      "recommendationTrend": {"trend": [{"strongBuy": 1, "buy": 4, "hold": 3, "sell": 1, "strongSell": 0}]},
      "majorHoldersBreakdown": {"insidersPercentHeld": {"raw": 0.02}},
    }
    with mock.patch.object(server, "build_history", return_value=([100 + index for index in range(260)], {"historySource": "test"})):
      dossier = server.build_stock_dossier("ICICIBANK.NS", snapshot, quote, summary, [100 + index for index in range(40)], [100 + index for index in range(260)])

    self.assertIn("daySnapshot", dossier)
    self.assertEqual(len(dossier["peerComparison"]), 5)
    self.assertGreaterEqual(len(dossier["benchmarkComparison"]), 3)
    self.assertIn("expertConsensus", dossier)
    self.assertTrue(dossier["influenceGraph"]["ledger"])

  def test_stock_dossier_unusual_activity_uses_documented_fallbacks(self):
    snapshot = {
      "symbol": "TEST",
      "exchange": "NASDAQ",
      "currency": "USD",
      "dataSource": "Unit quote",
      "price": 100,
      "previousClose": 0,
      "volume": 1000,
      "forecast": {"mae": 1.0},
    }
    quote = {"regularMarketOpen": 99}
    with mock.patch.object(server, "build_peer_comparison", return_value=[]), mock.patch.object(
      server, "benchmark_symbols_for_region", return_value=[]
    ), mock.patch.object(server, "build_influence_graph", return_value={"nodes": [], "edges": [], "ledger": []}):
      dossier = server.build_stock_dossier("TEST", snapshot, quote, {}, [100], [100])

    unusual = dossier["unusualActivity"]
    self.assertIsNone(unusual["twoDayMove"])
    self.assertIsNone(unusual["gapPercent"])
    self.assertIsNone(unusual["volumeRatio"])
    self.assertEqual(unusual["breakout"], "Range watch")
    self.assertEqual(unusual["metrics"]["twoDayMove"]["label"], "Unavailable")
    self.assertIn("Need at least 3", unusual["metrics"]["twoDayMove"]["status"])
    self.assertIn("Previous close missing", unusual["metrics"]["gapPercent"]["status"])
    self.assertIn("Average volume missing", unusual["metrics"]["volumeRatio"]["status"])
    self.assertIn("52W high unavailable", unusual["metrics"]["breakout"]["status"])

  def test_influence_graph_omits_unsourced_sensitive_claims(self):
    graph = server.build_influence_graph("TEST", {})

    self.assertEqual(graph["edges"], [])
    self.assertIn("Public cited", graph["policy"])

  def test_build_region_payload_contains_bonds_inflation_and_watchlist_implications(self):
    watchlist = [
      {"symbol": "AAPL", "name": "Apple", "exchange": "NASDAQ", "currency": "USD"},
      {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "exchange": "NSE", "currency": "INR"},
    ]
    payload = server.build_region_payload("us", watchlist, {"symbol": "AAPL", "exchange": "NASDAQ", "currency": "USD"})

    self.assertEqual(payload["region"], "us")
    self.assertIn("tenors", payload["bonds"])
    self.assertIn("headline", payload["inflation"])
    self.assertIn("cards", payload["watchlistImplications"])
    self.assertEqual(payload["watchlistImplications"]["cards"][0]["symbol"], "AAPL")
    self.assertIn("factorSchedule", payload["watchlistImplications"]["graph"])
    self.assertIn("papers", payload["watchlistImplications"]["graph"])
    self.assertIn("projects", payload["watchlistImplications"]["cards"][0])
    self.assertGreaterEqual(len(payload["watchlistImplications"]["cards"][0]["projects"]), 1)
    self.assertTrue(any(node.get("group") == "project" for node in payload["watchlistImplications"]["graph"]["nodes"]))
    self.assertIn("researchProtocol", payload)
    self.assertIn("factors", payload["researchProtocol"])
    self.assertIn("datasets", payload["researchProtocol"])

  def test_build_region_comparison_returns_cross_region_rows(self):
    comparison = server.build_region_comparison(
      {
        "us": server.build_region_payload("us", []),
        "india": server.build_region_payload("india", []),
      }
    )

    self.assertGreaterEqual(len(comparison["rows"]), 4)
    self.assertIn("US", comparison["summary"])

  def test_build_methodology_payload_contains_concepts_and_flow(self):
    # Use minimal stubs — no DB, no network needed for methodology payload
    snapshot = {
      "forecast": {"movingAverageSignal": {"state": "bullish"}, "direction": "up"},
      "decisionCockpit": {"stance": "Trend-following", "edgeScore": 72, "riskLevel": "Medium"},
      "eventFocus": {"label": "CPI release"},
      "decisionInputs": {"inputs": []},
      "researchOverview": {"cards": []},
    }
    region = {
      "analysis": {"driver": "bonds"},
      "researchProtocol": {},
      "watchlistImplications": {"graph": {"nodes": [], "links": []}},
    }

    payload = server.build_methodology_payload(snapshot, region)

    self.assertTrue(payload["concepts"])
    self.assertTrue(payload["flow"]["nodes"])
    self.assertTrue(payload["liveInputs"] is not None)
    # tradingPapers added — must be present and non-empty
    self.assertIn("tradingPapers", payload)
    self.assertGreater(len(payload["tradingPapers"]), 0)
    for paper in payload["tradingPapers"]:
      self.assertIn("title", paper)
      self.assertIn("year", paper)

  def test_research_participation_signal_is_centered_on_normal_volume(self):
    snapshot = {
      "symbol": "ICICIBANK.NS",
      "name": "ICICI Bank",
      "volume": 2_000_000,
      "stats": [{"label": "Avg volume", "value": "2.00M"}],
      "forecast": {
        "factorsRaw": {"fastMomentum": 0.0, "slowMomentum": 0.0},
        "eventPressure": 0.0,
        "models": {"classic": {"confidence": 60}},
      },
      "classicQuant": {"cards": [{"title": "Price z-score", "value": "+0.00"}]},
      "eventFocus": {"label": "None"},
      "sentiment": {"label": "Balanced"},
    }
    region = {
      "bonds": {"realYield": 1.2, "curve": {"slope2s10s": 0.1}},
      "inflation": {},
      "policy": {"centralBank": "RBI"},
    }

    overview = server.build_active_research_overview(snapshot, region)
    trend_card = next(card for card in overview["cards"] if card["label"] == "Trend + participation")

    self.assertEqual(server.parse_compact_number("2.00M"), 2_000_000)
    self.assertEqual(server.centered_volume_participation(1.0), 0.0)
    self.assertEqual(trend_card["value"], "+0.00")
    self.assertIn("VR 1.00x", trend_card["note"])

  def test_research_practices_report_implementation_coverage(self):
    annotated = server.annotate_practice_coverage(
      {
        "title": "Example paper",
        "requiredFactors": ["price history", "turnover", "nonexistent factor"],
      }
    )

    self.assertEqual(annotated["implementationStatus"], "Partial")
    self.assertIn("price history", annotated["implementedFactors"])
    self.assertIn("turnover", annotated["partialFactors"])
    self.assertIn("nonexistent factor", annotated["missingFactors"])

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

  def test_build_event_feed_includes_timestamps_and_significance(self):
    with mock.patch.object(
      server,
      "fetch_google_news_rss",
      return_value=[{"title": "Major partnership signed", "url": "https://example.com/story", "source": "example.com", "publishedAt": "2026-04-01T01:00:00+00:00"}],
    ), mock.patch.object(
      server,
      "fetch_popular_rss_items",
      return_value=[{"title": "BBC says partnership expands", "url": "https://example.com/bbc", "source": "BBC Business", "publishedAt": "2026-04-01T02:00:00+00:00"}],
    ), mock.patch.object(server, "duckduckgo_search", return_value=[]), mock.patch.object(server, "generate_local_llm_answer", return_value=None):
      payload = server.build_event_feed("partnerships", "ICICIBANK.NS")

    self.assertEqual(payload["category"], "partnerships")
    self.assertTrue(payload["asOf"])
    published_times = {item["publishedAt"] for item in payload["items"]}
    self.assertIn("2026-04-01T01:00:00+00:00", published_times)
    self.assertIn("2026-04-01T02:00:00+00:00", published_times)
    self.assertGreater(payload["items"][0]["significance"], 0)
    self.assertEqual(len(payload["items"]), 2)

  def test_build_event_feed_all_merges_categories_and_sorts_by_time(self):
    def fake_google(query):
      if "war news" in query:
        return [{"title": "War update", "url": "https://example.com/war", "source": "example.com", "publishedAt": "2026-04-01T03:00:00+00:00"}]
      if "business news" in query:
        return [{"title": "Business update", "url": "https://example.com/business", "source": "example.com", "publishedAt": "2026-04-01T01:00:00+00:00"}]
      return []

    with mock.patch.object(server, "fetch_google_news_rss", side_effect=fake_google), mock.patch.object(
      server,
      "fetch_popular_rss_items",
      return_value=[],
    ), mock.patch.object(
      server,
      "duckduckgo_search",
      return_value=[],
    ), mock.patch.object(server, "generate_local_llm_answer", return_value=None):
      payload = server.build_event_feed("all", "ICICIBANK.NS")

    self.assertEqual(payload["category"], "all")
    self.assertGreaterEqual(len(payload["items"]), 2)
    self.assertEqual(payload["items"][0]["title"], "War update")
    self.assertEqual(payload["items"][0]["category"], "war")
    self.assertEqual(payload["items"][1]["category"], "business")

  def test_filter_market_relevant_items_drops_local_crime_noise(self):
    items = [
      {"title": "City police investigate downtown robbery", "source": "Local News", "publishedAt": "2026-04-01T01:00:00+00:00"},
      {"title": "Oil prices jump as sanctions raise shipping risk", "source": "Market Desk", "publishedAt": "2026-04-01T02:00:00+00:00"},
    ]

    filtered = server.filter_market_relevant_items(items, "world", "ICICIBANK.NS")

    self.assertEqual(len(filtered), 1)
    self.assertIn("Oil prices jump", filtered[0]["title"])

  def test_radar_priority_prefers_fresher_market_relevant_story(self):
    fresh = {
      "title": "Oil jumps after sanctions raise shipping risk",
      "source": "BBC Business",
      "publishedAt": "2026-04-01T10:00:00+00:00",
      "category": "world",
    }
    stale = {
      "title": "Generic geopolitical essay",
      "source": "Unknown Source",
      "publishedAt": "2026-03-01T10:00:00+00:00",
      "category": "world",
    }

    self.assertGreater(server.radar_priority_score(fresh, "ICICIBANK.NS"), server.radar_priority_score(stale, "ICICIBANK.NS"))

  def test_fetch_popular_rss_items_merges_configured_category_feeds(self):
    with mock.patch.object(
      server,
      "fetch_rss_feed",
      side_effect=[
        [{"title": "BBC business update", "url": "https://example.com/bbc", "source": "BBC Business", "publishedAt": "2026-04-01T00:00:00+00:00"}],
        [{"title": "NPR business update", "url": "https://example.com/npr", "source": "NPR Business", "publishedAt": "2026-04-01T01:00:00+00:00"}],
      ],
    ):
      items = server.fetch_popular_rss_items("business")

    self.assertEqual(len(items), 2)
    self.assertEqual(items[0]["source"], "BBC Business")
    self.assertEqual(items[1]["source"], "NPR Business")


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
      "eventFocus": {"category": "business", "label": "Business", "reason": "Business and earnings updates are the main drivers behind the current move."},
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
    self.assertEqual(payload["active"]["eventFocus"]["category"], "business")
    self.assertIn("researchOverview", payload["active"])
    self.assertIn("cards", payload["active"]["researchOverview"])


if __name__ == "__main__":
  unittest.main()
