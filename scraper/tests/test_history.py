import copy
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta

from scraper.collector import run
from scraper.history import ingest, open_database, review


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "examples" / "fixture-source.json"


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "candidates.json"
        self.assertEqual(run(CONFIG, self.out), 0)
        self.payload = json.loads(self.out.read_text())
        self.db = open_database(Path(self.tmp.name) / "data" / "prices.sqlite")
        self.addCleanup(self.db.close)

    def test_ingest_is_idempotent_and_preserves_reviews(self):
        self.assertEqual(ingest(self.db, self.payload), (2, 2))
        cid = self.payload["candidates"][0]["candidateId"]
        review(self.db, cid, "approved")
        self.assertEqual(ingest(self.db, self.payload), (2, 0))
        row = self.db.execute(
            "SELECT review_status FROM candidates WHERE candidate_id = ?", (cid,)
        ).fetchone()
        self.assertEqual(row, ("approved",))
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM price_observations").fetchone()[0], 2)

    def test_observes_changes_in_price_history(self):
        ingest(self.db, self.payload)
        later = copy.deepcopy(self.payload)
        later["generatedAt"] = (datetime.fromisoformat(self.payload["generatedAt"]) + timedelta(days=1)).isoformat()
        later["candidates"][0]["priceAmount"] = "119.99"
        self.assertEqual(ingest(self.db, later), (2, 2))
        cid = later["candidates"][0]["candidateId"]
        self.assertEqual(
            [x[0] for x in self.db.execute(
                "SELECT amount FROM price_observations WHERE candidate_id = ? ORDER BY observed_at", (cid,)
            ).fetchall()],
            ["129.99", "119.99"],
        )

    def test_invalid_snapshot_never_commits_partial_data(self):
        invalid = copy.deepcopy(self.payload)
        invalid["candidates"][1]["priceAmount"] = "-10.00"
        with self.assertRaises(ValueError):
            ingest(self.db, invalid)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM candidates").fetchone()[0], 0)
        invalid = copy.deepcopy(self.payload)
        invalid["errors"] = [{"sourceId": "example", "error": "crawl failed"}]
        with self.assertRaises(ValueError):
            ingest(self.db, invalid)

    def test_currency_change_rejected(self):
        ingest(self.db, self.payload)
        changed = copy.deepcopy(self.payload)
        changed["candidates"][0]["currency"] = "EUR"
        with self.assertRaises(ValueError):
            ingest(self.db, changed)

    def test_older_snapshot_preserves_latest_metadata(self):
        newer = copy.deepcopy(self.payload)
        newer["generatedAt"] = "2026-11-25T12:00:00+00:00"
        older = copy.deepcopy(self.payload)
        older["generatedAt"] = "2026-11-24T12:00:00-05:00"
        older["candidates"][0]["title"] = "Old title"
        ingest(self.db, newer)
        ingest(self.db, older)
        row = self.db.execute("SELECT title, first_seen, last_seen FROM candidates WHERE candidate_id=?", (newer["candidates"][0]["candidateId"],)).fetchone()
        self.assertEqual(row, (newer["candidates"][0]["title"], "2026-11-24T17:00:00+00:00", "2026-11-25T12:00:00+00:00"))

    def test_manual_approval_requires_known_candidate(self):
        ingest(self.db, self.payload)
        with self.assertRaises(ValueError):
            review(self.db, "unknown", "approved")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM candidates WHERE review_status='approved'").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
