import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HtmlContractTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    cls.index_html = (ROOT / "index.html").read_text()
    cls.app_js = (ROOT / "app.js").read_text()
    cls.readme = (ROOT / "README.md").read_text()

  def test_index_contains_core_dashboard_targets(self):
    required_ids = [
      "radar-hotspots",
      "data-flow-bar",
      "radar-source-note",
      "overview-board",
      "stock-dossier-panel",
      "stock-dossier-nav",
      "stock-dossier",
      "market-discovery",
      "bond-summary",
      "bond-curve",
      "inflation-cards",
      "policy-cards",
      "equity-summary",
      "sector-grid",
      "macro-events-list",
      "macro-watch-next",
      "methodology-headline",
      "methodology-cockpit",
      "methodology-live-inputs",
      "methodology-concepts",
      "methodology-flowchart",
      "watchlist-implication-cards",
      "impact-graph-detail",
      "impact-graph",
      "comparison-table",
      "recent-tickers",
      "quote-source-note",
      "market-session-strip",
      "model-agreement-note",
    ]
    for target in required_ids:
      self.assertIn(f'id="{target}"', self.index_html)

  def test_index_contains_expected_top_level_tabs(self):
    tabs = re.findall(r'data-tab="([^"]+)"', self.index_html)
    self.assertEqual(tabs, ["overview", "bond-market", "inflation", "equity-context", "events-calendar", "methodology", "watchlist-implications", "comparison"])

  def test_topbar_macro_title_and_live_market_header_removed(self):
    self.assertNotIn("Live Markets", self.index_html)
    self.assertNotIn("macro, bonds, inflation, equities, and watchlist context", self.app_js)
    self.assertNotIn("NASDAQ, S&amp;P 500, NSE, and global market coverage", self.index_html)
    self.assertNotIn("<header class=\"topbar\">", self.index_html)
    self.assertIn("global-market-head-actions", self.app_js)
    self.assertIn("status-updated", self.app_js)

  def test_frontend_contains_key_renderers_and_handlers(self):
    expected_snippets = [
      "function nextFrame(",
      "function deferWork(",
      "function renderBanner()",
      "function renderOverview()",
      "function renderBondMarket()",
      "function renderInflationView()",
      "function renderEquityContext()",
      "function renderMacroEvents()",
      "function renderMethodology()",
      "function renderWatchlistImplications()",
      "function renderComparison()",
      "function renderCorePanels()",
      "function renderDeferredPanels()",
      "function loadEventFeed(",
      "function liveStatusClusterMarkup(",
      "eventCache",
      "event-card-header",
      "dashboardRequestId",
      "selectedRegion",
      "function renderImpactGraphWorkspace(",
      "decision-cockpit-card",
      "function logNonAbort(",
      "methodology-cockpit-hero",
      "function renderStockDossier(",
      "DOSSIER_CARD_META",
      "data-flow-bar",
      "function renderDataFlowBar(",
      "function pollHistoryProgress(",
      "function scheduleDataFlowAutoHide(",
      "is-peek",
      "function renderMetricCommandCard(",
      "Unavailable",
      "function setupDossierDrag(",
      "dossierOrder",
      "stockDossier",
      "Peer comparison",
      "range-watch-stack",
      "Market discovery",
      "sector-matrix-benchmark",
      "sector-tile-top",
      "sector-tile-meta",
      "chart-mode-tab",
      "function buildSyntheticCandles(",
      "function buildImpactGraphPresetPositions(",
      "function relayoutImpactGraph(",
      "pendingImpactGraph",
      "formatAxisDate",
    ]
    for snippet in expected_snippets:
      self.assertIn(snippet, self.app_js)

  def test_cloud_controls_removed_but_news_ticker_remains(self):
    self.assertNotIn("pop-radar-clouds", self.index_html)
    self.assertNotIn("cloud-puff", self.index_html)
    self.assertNotIn("radar-floats", self.index_html)
    self.assertNotIn("cloud-puff", self.app_js)
    self.assertNotIn("floating event clouds", self.readme)
    self.assertNotIn("Radar Cloud Layer", self.readme)
    self.assertNotIn("radar clouds can be popped", self.readme)
    self.assertIn("headline-track", self.index_html)
    self.assertIn("ticker-track", self.index_html)

  def test_readme_documents_architecture_and_test_entrypoint(self):
    self.assertIn("## Technical Summary", self.readme)
    self.assertIn("## Architecture", self.readme)
    self.assertIn("auto-masonry card layout", self.readme)
    self.assertIn("Sector matrix", self.readme)
    self.assertIn("Wilder RSI", self.readme)

  def test_sector_matrix_uses_readable_responsive_tiles(self):
    styles = (ROOT / "styles.css").read_text()

    self.assertIn("minmax(min(100%, 190px), 1fr)", styles)
    self.assertIn("min-height: 132px", styles)
    self.assertIn("font-size: 1.42rem", styles)
    self.assertIn("grid-template-columns: 1fr", styles)

  def test_overview_chart_modes_and_sector_strip_are_readable(self):
    styles = (ROOT / "styles.css").read_text()

    for chart_type in ["line", "area", "candles", "bars"]:
      self.assertIn(f'data-chart-type="{chart_type}"', self.index_html)
    self.assertIn("chartType: \"line\"", self.app_js)
    self.assertIn("chartType === \"candles\"", self.app_js)
    self.assertIn("chartType === \"bars\"", self.app_js)
    self.assertIn("repeat(auto-fit, minmax(142px, 1fr))", styles)
    self.assertIn("font-size: 0.86rem", styles)
    self.assertIn("Financial Services", self.app_js)

  def test_watchlist_graph_defers_until_visible(self):
    styles = (ROOT / "styles.css").read_text()

    self.assertIn("state.pendingImpactGraph = graph", self.app_js)
    self.assertIn("panel?.classList.contains(\"active\")", self.app_js)
    self.assertIn("renderWatchlistImplications();", self.app_js)
    self.assertIn("relayoutImpactGraph();", self.app_js)
    self.assertIn("name: \"preset\"", self.app_js)
    self.assertIn("fit-all view, zoom for detail", self.app_js)
    self.assertIn("minZoom: 0.25", self.app_js)
    self.assertIn("maxZoom: 3", self.app_js)
    self.assertIn(">Fit all<", self.index_html)
    self.assertIn(">Detail +<", self.index_html)
    self.assertIn("height: clamp(520px, 62vh, 680px)", styles)


if __name__ == "__main__":
  unittest.main()
