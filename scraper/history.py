"""Persist scraped candidate prices and editorial decisions separately from the storefronts."""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS candidates (
  candidate_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  site TEXT NOT NULL,
  merchant TEXT NOT NULL,
  title TEXT NOT NULL,
  product_url TEXT NOT NULL,
  currency TEXT NOT NULL,
  review_status TEXT NOT NULL DEFAULT 'pending'
    CHECK(review_status IN ('pending', 'approved', 'rejected')),
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS price_observations (
  candidate_id TEXT NOT NULL REFERENCES candidates(candidate_id),
  observed_at TEXT NOT NULL,
  amount TEXT NOT NULL,
  PRIMARY KEY (candidate_id, observed_at)
);
CREATE INDEX IF NOT EXISTS observations_by_date
  ON price_observations(observed_at);
"""


def open_database(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    return db


def _validate_timestamp(raw: str) -> str:
    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is None:
        raise ValueError("generatedAt must contain a timezone")
    return parsed.isoformat()


def _validate_candidate(row: dict) -> dict:
    required = ("candidateId", "sourceId", "site", "merchant", "title",
                "productUrl", "priceAmount", "currency")
    if not isinstance(row, dict) or any(not isinstance(row.get(k), str) or not row[k] for k in required):
        raise ValueError("Candidate has missing required string fields")
    try:
        price = Decimal(row["priceAmount"])
    except InvalidOperation as exc:
        raise ValueError("Invalid priceAmount") from exc
    if not price.is_finite() or price <= 0:
        raise ValueError("priceAmount must be positive and finite")
    if row["site"] not in ("adventures", "personal-training", "solutions"):
        raise ValueError("Invalid site")
    if len(row["currency"]) != 3 or not row["currency"].isalpha():
        raise ValueError("Invalid currency code")
    if not row["productUrl"].startswith("https://"):
        raise ValueError("productUrl must use HTTPS")
    return row


def ingest(db: sqlite3.Connection, payload: dict) -> tuple[int, int]:
    """Import an observation snapshot atomically; never overwrite editorial status."""
    when = _validate_timestamp(payload["generatedAt"])
    rows = payload.get("candidates")
    if not isinstance(rows, list) or payload.get("errors"):
        raise ValueError("Refusing incomplete or failed source snapshots")
    validated = [_validate_candidate(row) for row in rows]
    inserted = 0
    with db:
        for row in validated:
            values = (row["candidateId"], row["sourceId"], row["site"],
                      row["merchant"], row["title"], row["productUrl"],
                      row["currency"], when, when)
            db.execute(
                """INSERT OR IGNORE INTO candidates
                   (candidate_id, source_id, site, merchant, title, product_url,
                    currency, first_seen, last_seen) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                values,
            )
            db.execute(
                """UPDATE candidates SET last_seen = ?, title = ?
                   WHERE candidate_id = ?""",
                (when, row["title"], row["candidateId"]),
            )
            cursor = db.execute(
                """INSERT OR IGNORE INTO price_observations
                   (candidate_id, observed_at, amount) VALUES (?, ?, ?)""",
                (row["candidateId"], when, row["priceAmount"]),
            )
            inserted += cursor.rowcount
    return len(validated), inserted


def review(db: sqlite3.Connection, candidate_id: str, decision: str) -> None:
    if decision not in ("approved", "rejected", "pending"):
        raise ValueError("Invalid editorial decision")
    with db:
        cursor = db.execute(
            "UPDATE candidates SET review_status = ? WHERE candidate_id = ?",
            (decision, candidate_id),
        )
    if cursor.rowcount != 1:
        raise ValueError("Candidate not found")


def main() -> int:
    parser = argparse.ArgumentParser(description="Store candidate price history and review decisions")
    parser.add_argument("--db", type=Path, required=True, help="Persistent SQLite DB path")
    commands = parser.add_subparsers(dest="command", required=True)
    imports = commands.add_parser("import")
    imports.add_argument("--input", type=Path, required=True)
    decisions = commands.add_parser("review")
    decisions.add_argument("--candidate-id", required=True)
    decisions.add_argument("--status", choices=["approved", "rejected", "pending"], required=True)
    args = parser.parse_args()
    try:
        with open_database(args.db) as db:
            if args.command == "import":
                payload = json.loads(args.input.read_text(encoding="utf-8"))
                candidates, inserted = ingest(db, payload)
                print(f"Imported {candidates} candidates; {inserted} new price observations")
            else:
                review(db, args.candidate_id, args.status)
                print(f"Candidate {args.candidate_id} set to {args.status}")
    except (ValueError, KeyError, OSError, sqlite3.Error) as exc:
        parser.exit(status=1, message=f"History operation failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
