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
      "starfield",
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
      "toggle-detail-mode",
      "ticker-search-button",
      "market-heat-map-group",
      "market-heat-map-sector",
      "market-heat-map-scope",
      "market-heat-map-size",
      "market-heat-map-limit",
      "market-heat-map-expand",
    ]
    for target in required_ids:
      self.assertIn(f'id="{target}"', self.index_html)

  def test_index_contains_expected_top_level_tabs(self):
    tabs = re.findall(r'data-tab="([^"]+)"', self.index_html)
    self.assertEqual(tabs, ["overview", "bond-market", "inflation", "equity-context", "events-calendar", "methodology", "watchlist-implications", "comparison"])

  def test_market_discovery_sits_before_heatmap_and_dossier(self):
    discovery_index = self.index_html.index('id="market-discovery"')
    heatmap_index = self.index_html.index('id="market-heat-map-panel"')
    dossier_index = self.index_html.index('id="stock-dossier-panel"')

    self.assertLess(discovery_index, heatmap_index)
    self.assertLess(heatmap_index, dossier_index)

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
      "searchRequestId",
      "selectedRegion",
      "function renderImpactGraphWorkspace(",
      "decision-cockpit-card",
      "function logNonAbort(",
      "methodology-cockpit-hero",
      "function renderStockDossier(",
      "DOSSIER_CARD_META",
      "SMA 5-200",
      "simpleDossierKeys = [\"day\", \"ma\", \"activity\", \"benchmarks\"]",
      "data-flow-bar",
      "function renderDataFlowBar(",
      "function initStarfieldParallax(",
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
      "function groupMarketHeatMapTiles(",
      "function marketHeatMapSectorDetail(",
      "data-heat-open-group",
      "function scheduleHeatMapHistoryWarmup(",
      "usableQuotes",
      "market-heat-group",
      "chart-mode-tab",
      "function buildSyntheticCandles(",
      "function buildImpactGraphPresetPositions(",
      "function relayoutImpactGraph(",
      "pendingImpactGraph",
      "formatAxisDate",
    ]
    for snippet in expected_snippets:
      self.assertIn(snippet, self.app_js)

  def test_dossier_layout_guards_exist(self):
    styles = (ROOT / "styles.css").read_text()
    expected_snippets = [
      "body:not(.detail-mode) #dossier-benchmarks",
      "grid-column: 1 / -1",
      ".ma-dossier-list em small",
      ".dossier-card-title strong",
      "text-overflow: ellipsis",
      "Reliability beats decoration",
      ".scroll-reveal.is-visible",
      ".market-heat-map-panel.is-expanded",
      ".market-heat-group-grid",
      ".market-heat-sector-detail",
      ".market-heat-company-table",
    ]
    for snippet in expected_snippets:
      self.assertIn(snippet, styles)

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

  def test_dashboard_boots_progressively_while_full_refresh_loads(self):
    self.assertIn("function markDashboardInteractive(", self.app_js)
    self.assertIn("markDashboardInteractive(\"Live quote loaded\")", self.app_js)
    self.assertIn("financial-board-dashboard-cache-v2", self.app_js)
    self.assertIn("function saveDashboardCache(", self.app_js)
    self.assertIn("function loadDashboardCache(", self.app_js)
    self.assertIn("hydrateDashboardFromPayload(cachedDashboard", self.app_js)
    self.assertIn("refreshDashboard({ primeFast: false, primeRadar: false })", self.app_js)
    self.assertIn("loadRadar({ silent: true }).catch", self.app_js)
    self.assertIn("loadGlobalMarkets({ silent: true }).catch", self.app_js)
    self.assertIn("refreshDashboard().catch", self.app_js)
    self.assertIn("function startOverviewRefresh(", self.app_js)
    self.assertIn("function startGlobalMarketsRefresh(", self.app_js)
    self.assertIn("function startDashboardRefresh(", self.app_js)
    self.assertIn("function scheduleHistoryProgressPoll(", self.app_js)
    self.assertIn("function quoteFreshnessForDisplay(", self.app_js)
    self.assertIn("function exchangeTimeZoneForItem(", self.app_js)
    self.assertIn("function setDetailMode(", self.app_js)
    self.assertIn("financial-board-detail-mode", self.app_js)
    self.assertIn("exchange print", self.app_js)
    self.assertIn("Historical fallback", self.app_js)
    self.assertIn("function mergeQuoteIntoActiveHistory(", self.app_js)
    self.assertIn("normalizedRange === \"3D\" || normalizedRange === \"5D\"", self.app_js)

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
    self.assertIn("chartTimeZone(options)", self.app_js)
    self.assertIn("exchangeTimeZoneForItem(options.item", self.app_js)
    self.assertIn("shouldRedrawLiveChart()", self.app_js)
    self.assertIn("appendGap = normalizedRange === \"1D\" ? 5_000 : 15_000", self.app_js)
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
