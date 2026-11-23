import json
import tempfile
import unittest
from pathlib import Path

from scrapling import Selector

from scraper.collector import extract, hostname_allowed, money, run


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "examples" / "fixture-source.json"


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads(CONFIG.read_text())["sources"][0]
        self.fixture = (ROOT / "tests" / "fixtures" / "demo-store.html").read_text()

    def test_extract_only_valid_items(self):
        candidates = extract(self.source, Selector(content=self.fixture))
        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0]["priceAmount"], "129.99")
        self.assertEqual(candidates[0]["regularPriceAmount"], "189.99")
        self.assertEqual(candidates[1]["priceAmount"], "1049.50")
        self.assertIsNone(candidates[1]["regularPriceAmount"])
        self.assertEqual(candidates[0]["reviewStatus"], "pending")
        self.assertEqual(candidates[0]["productUrl"], "https://example.com/products/solar-panel")

    def test_price_parser(self):
        self.assertEqual(money("$1,250.00"), "1250.00")
        self.assertIsNone(money("Check price"))
        self.assertIsNone(money("$0.00"))

    def test_url_allowlist(self):
        self.assertTrue(hostname_allowed("https://example.com/product", ["example.com"]))
        self.assertFalse(hostname_allowed("http://example.com", ["example.com"]))
        self.assertFalse(hostname_allowed("https://example.com.attacker.test/", ["example.com"]))
        self.assertFalse(hostname_allowed("https://127.0.0.1", ["127.0.0.1"]))
        self.assertFalse(hostname_allowed("https://localhost", ["localhost"]))

    def test_collect_fixture_creates_candidate_file_only(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "candidates.json"
            self.assertEqual(run(CONFIG, output), 0)
            data = json.loads(output.read_text())
            self.assertEqual(len(data["candidates"]), 2)
            self.assertEqual(data["errors"], [])
            self.assertNotIn("status", data["candidates"][0])

    def test_http_requires_explicit_opt_in(self):
        source = {**self.source, "mode": "http"}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.json"
            path.write_text(json.dumps({"sources": [source]}))
            output = Path(folder) / "candidates.json"
            self.assertEqual(run(path, output), 1)
            self.assertIn("Live crawling disabled", output.read_text())


if __name__ == "__main__":
    unittest.main()
