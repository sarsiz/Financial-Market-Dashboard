import importlib.util
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check_repo_safety.py"
SPEC = importlib.util.spec_from_file_location("check_repo_safety", MODULE_PATH)
repo_safety = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(repo_safety)


class RepositorySafetyTests(unittest.TestCase):
  def test_private_market_and_broker_paths_are_forbidden(self):
    private_paths = [
      ".env",
      ".env.local",
      "config.json",
      "financial_board.db",
      "data/history.json",
      "kb/companies/private.md",
      "vault/market-map/session.md",
      ".kite/session.json",
      "kite_session.json",
      "zerodha_credentials.json",
    ]
    for path in private_paths:
      with self.subTest(path=path):
        self.assertTrue(repo_safety.is_forbidden_path(path))

    self.assertFalse(repo_safety.is_forbidden_path(".env.example"))
    self.assertFalse(repo_safety.is_forbidden_path("data/.gitkeep"))
    self.assertFalse(repo_safety.is_forbidden_path("kb/regions/.gitkeep"))

  def test_literal_kite_credentials_are_detected_without_echoing_values(self):
    field = b"kite_" + b"access_token"
    value = b"live-broker-" + b"token-value-12345"
    raw = field + b' = "' + value + b'"\n'
    findings = repo_safety.scan_text("example.py", raw)

    self.assertEqual(len(findings), 1)
    self.assertIn("literal broker credential", findings[0])
    self.assertNotIn("live-broker-token", findings[0])

  def test_documented_placeholders_are_allowed(self):
    raw = b'api_secret = "your_api_secret"\nrequest_token = "request_token_here"\n'
    self.assertEqual(repo_safety.scan_text("example.py", raw), [])

  def test_current_tracked_tree_passes_safety_check(self):
    completed = subprocess.run(
      ["python3", str(MODULE_PATH)],
      cwd=ROOT,
      text=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      check=False,
    )
    self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
  unittest.main()
