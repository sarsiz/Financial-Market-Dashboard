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
      "recent-tickers",
      "quote-source-note",
      "market-session-strip",
      "model-agreement-note",
      "lab-form",
      "lab-chart",
      "academy-cards",
      "academy-ticker-brief",
      "academy-source-list",
      "glossary-list",
      "research-list",
    ]
    for target in required_ids:
      self.assertIn(f'id="{target}"', self.index_html)

  def test_index_contains_expected_top_level_tabs(self):
    tabs = re.findall(r'data-tab="([^"]+)"', self.index_html)
    self.assertEqual(tabs, ["overview", "lab", "academy", "research"])

  def test_frontend_contains_key_renderers_and_handlers(self):
    expected_snippets = [
      "function nextFrame(",
      "function deferWork(",
      "function renderBanner()",
      "function renderOverview()",
      "function renderLab()",
      "function renderCorePanels()",
      "function renderDeferredPanels()",
      "function loadAcademyDetail(",
      "event-brief-note",
      "event-card-header",
      "dashboardRequestId",
      "academyRequestId",
      "function buildRadarFloatItems",
      'document.getElementById("lab-form").addEventListener("submit"',
      "state.radarFloatOpenId",
    ]
    for snippet in expected_snippets:
      self.assertIn(snippet, self.app_js)

  def test_readme_documents_architecture_and_test_entrypoint(self):
    self.assertIn("## Technical Summary", self.readme)
    self.assertIn("## Architecture", self.readme)


if __name__ == "__main__":
  unittest.main()
