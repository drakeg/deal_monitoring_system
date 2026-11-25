import copy
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta

from scraper.collector import run
from scraper.history import ingest, open_database, review
from scraper.insights import report

ROOT = Path(__file__).resolve().parents[1]

class InsightsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        output = Path(self.temp.name) / "candidates.json"
        self.assertEqual(run(ROOT / "examples" / "fixture-source.json", output), 0)
        self.payload = json.loads(output.read_text())
        self.db = open_database(Path(self.temp.name) / "history.sqlite")
        self.addCleanup(self.db.close)

    def test_single_observation_never_claims_discount(self):
        ingest(self.db, self.payload)
        rows = report(self.db)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(not row["newObservedLow"] for row in rows))
        self.assertTrue(all(row["claimVerified"] is False for row in rows))

    def test_new_observed_low_is_based_on_history_not_msrp(self):
        ingest(self.db, self.payload)
        later = copy.deepcopy(self.payload)
        later["generatedAt"] = (datetime.fromisoformat(self.payload["generatedAt"]) + timedelta(days=1)).isoformat()
        later["candidates"][0]["priceAmount"] = "119.99"
        later["candidates"][1]["priceAmount"] = "1099.00"
        ingest(self.db, later)
        rows = {row["candidateId"]: row for row in report(self.db)}
        low = rows[later["candidates"][0]["candidateId"]]
        high = rows[later["candidates"][1]["candidateId"]]
        self.assertTrue(low["newObservedLow"])
        self.assertEqual(low["previousObservedLow"], "129.99")
        self.assertEqual(low["dropFromPreviousLow"], "10.00")
        self.assertEqual(low["dropPercent"], "7.7")
        self.assertFalse(low["claimVerified"])
        self.assertFalse(high["newObservedLow"])
        self.assertIsNone(high["dropPercent"])

    def test_review_state_remains_unchanged(self):
        ingest(self.db, self.payload)
        cid = self.payload["candidates"][0]["candidateId"]
        review(self.db, cid, "approved")
        row = next(x for x in report(self.db) if x["candidateId"] == cid)
        self.assertEqual(row["reviewStatus"], "approved")
        self.assertEqual(self.db.execute("SELECT review_status FROM candidates WHERE candidate_id=?", (cid,)).fetchone(), ("approved",))

    def test_reject_insufficient_observations(self):
        with self.assertRaises(ValueError):
            report(self.db, min_observations=1)

if __name__ == "__main__":
    unittest.main()
