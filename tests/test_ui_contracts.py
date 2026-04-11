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
      "radar-floats",
      "radar-hotspots",
      "radar-source-note",
      "overview-board",
      "region-selector",
      "bond-summary",
      "bond-curve",
      "inflation-cards",
      "policy-cards",
      "equity-summary",
      "sector-grid",
      "macro-events-list",
      "macro-watch-next",
      "watchlist-implication-cards",
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
    self.assertEqual(tabs, ["overview", "bond-market", "inflation", "equity-context", "events-calendar", "watchlist-implications", "comparison"])

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
      "function renderWatchlistImplications()",
      "function renderComparison()",
      "function renderRegionSelector()",
      "function renderCorePanels()",
      "function renderDeferredPanels()",
      "function loadEventFeed(",
      "eventCache",
      "event-card-header",
      "dashboardRequestId",
      "selectedRegion",
      "function buildRadarFloatItems",
      "state.radarFloatOpenId",
    ]
    for snippet in expected_snippets:
      self.assertIn(snippet, self.app_js)

  def test_readme_documents_architecture_and_test_entrypoint(self):
    self.assertIn("## Technical Summary", self.readme)
    self.assertIn("## Architecture", self.readme)


if __name__ == "__main__":
  unittest.main()
