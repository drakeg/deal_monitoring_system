"""Read-only deal insights from verified historical observations.

The first observation is a baseline, not a discount. Only actual historical
observations from the same product and currency are compared.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from scraper.history import open_database

def report(db: sqlite3.Connection, *, min_observations: int = 2) -> list[dict]:
    if min_observations < 2:
        raise ValueError("At least two historical observations required")
    candidates = db.execute(
        """SELECT candidate_id, site, merchant, title, product_url, currency,
                  review_status, last_seen
           FROM candidates ORDER BY site, merchant, candidate_id"""
    ).fetchall()
    results = []
    for cid, site, merchant, title, url, currency, status, last_seen in candidates:
        rows = db.execute(
            """SELECT observed_at, amount FROM price_observations
               WHERE candidate_id = ? ORDER BY observed_at ASC""",
            (cid,),
        ).fetchall()
        if not rows:
            continue
        amounts = [Decimal(amount) for _, amount in rows]
        current = amounts[-1]
        previous = amounts[:-1]
        baseline = min(previous) if previous else None
        # A genuine observed low is useful; an arbitrary crossed-out MSRP isn't.
        is_new_low = len(amounts) >= min_observations and baseline is not None and current < baseline
        saving = baseline - current if is_new_low else Decimal("0")
        pct = (saving / baseline * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) if is_new_low else Decimal("0")
        results.append({
            "candidateId": cid,
            "site": site,
            "merchant": merchant,
            "title": title,
            "productUrl": url,
            "currency": currency,
            "reviewStatus": status,
            "observations": len(rows),
            "lastSeen": last_seen,
            "latestObservedPrice": str(current),
            "previousObservedLow": str(baseline) if baseline is not None else None,
            "newObservedLow": bool(is_new_low),
            "dropFromPreviousLow": str(saving) if is_new_low else None,
            "dropPercent": str(pct) if is_new_low else None,
            "claimVerified": False,
        })
    return results

def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only historical price insight report")
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON report destination")
    parser.add_argument("--min-observations", type=int, default=2)
    args = parser.parse_args()
    if not args.db.is_file():
        parser.error("Database does not exist; ingest a snapshot first")
    with open_database(args.db) as db:
        data = report(db, min_observations=args.min_observations)
    rendered = json.dumps({"insights": data}, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
