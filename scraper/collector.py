"""Scrapling-powered candidate extractor; never writes storefront deal data.

Only fixture sources run by default. Live HTTP requires --allow-live,
an explicit domain allowlist, HTTPS and robots.txt permission.
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

from scrapling import Selector

USER_AGENT = "MadMallardDealMonitor/0.1"
SITES = {"adventures", "personal-training", "solutions"}
PRICE = re.compile(r"(?<!\d)(\d{1,3}(?:,\d{3})+|\d+)\.(\d{2})(?!\d)")


def hostname_allowed(url: str, allowed_domains: list[str]) -> bool:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return False
    if parsed.port not in (None, 443):
        return False
    hostname = parsed.hostname.lower().rstrip(".")
    if hostname not in {name.lower().rstrip(".") for name in allowed_domains}:
        return False
    try:
        if not ipaddress.ip_address(hostname).is_global:
            return False
    except ValueError:
        if "." not in hostname or hostname.endswith((".local", ".internal", ".localhost")):
            return False
    return True


def money(raw: str | None) -> str | None:
    if not raw:
        return None
    match = PRICE.search(raw)
    if not match:
        return None
    try:
        amount = Decimal(match.group(1).replace(",", "") + "." + match.group(2))
        return str(amount) if amount > 0 else None
    except InvalidOperation:
        return None


def extract(source: dict, page: Selector) -> list[dict]:
    selectors = source["selectors"]
    items = page.css(selectors["item"])
    result: list[dict] = []
    seen: set[str] = set()
    for item in items:
        def get(field: str) -> str:
            expression = selectors.get(field)
            return str(item.css(expression).get() or "").strip() if expression else ""

        title = get("title")
        price = money(get("price"))
        target = urljoin(source["listingUrl"], get("url"))
        if not title or not price or not get("url"):
            continue
        if not hostname_allowed(target, source["allowedDomains"]):
            continue
        parts = urlsplit(target)
        product_url = urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))
        unique = source["id"] + "|" + product_url
        if unique in seen:
            continue
        seen.add(unique)
        previous = money(get("regularPrice"))
        result.append({
            "candidateId": hashlib.sha256(unique.encode("utf-8")).hexdigest()[:20],
            "site": source["site"],
            "sourceId": source["id"],
            "merchant": source["merchant"],
            "title": title,
            "productUrl": product_url,
            "priceAmount": price,
            "currency": source.get("currency", "USD"),
            "regularPriceAmount": previous if previous and Decimal(previous) > Decimal(price) else None,
            "reviewStatus": "pending",
        })
    return result


def robots_allowed(url: str) -> bool:
    parts = urlsplit(url)
    robots_url = urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))
    try:
        with urlopen(Request(robots_url, headers={"User-Agent": USER_AGENT}), timeout=12) as response:
            lines = response.read(524288).decode("utf-8", "replace").splitlines()
    except HTTPError as exc:
        if exc.code == 404:
            return True
        return False
    except OSError:
        return False
    robot = RobotFileParser()
    robot.parse(lines)
    return bool(robot.can_fetch(USER_AGENT, url))


def validate_source(source: dict) -> None:
    if source.get("site") not in SITES:
        raise ValueError("Invalid site")
    if not source.get("id") or not source.get("merchant"):
        raise ValueError("Source id and merchant required")
    domains = source.get("allowedDomains")
    if not isinstance(domains, list) or not domains:
        raise ValueError("Explicit allowedDomains required")
    if not hostname_allowed(source.get("listingUrl", ""), domains):
        raise ValueError("Listing URL must use HTTPS and an allowed public domain")
    selectors = source.get("selectors")
    if not isinstance(selectors, dict) or not all(selectors.get(k) for k in ("item", "title", "price", "url")):
        raise ValueError("item/title/price/url selectors required")
    if source.get("mode") not in ("fixture", "http"):
        raise ValueError("mode must be fixture or http")


def fetch_source(source: dict, config_dir: Path, allow_live: bool) -> Selector:
    if source["mode"] == "fixture":
        fixture = source.get("fixturePath")
        if not fixture:
            raise ValueError("Fixture mode requires fixturePath")
        return Selector(text=(config_dir / fixture).read_text(encoding="utf-8"))
    if not allow_live:
        raise ValueError("Live crawling disabled; pass --allow-live explicitly")
    if not robots_allowed(source["listingUrl"]):
        raise ValueError("robots.txt disallows crawling or could not be verified")
    # No stealth browser/proxy/CAPTCHA bypass, and no automatic redirects.
    from scrapling.fetchers import Fetcher
    response = Fetcher.get(
        source["listingUrl"],
        stealthy_headers=False,
        follow_redirects=False,
        headers={"User-Agent": USER_AGENT},
        timeout=20,
        retries=2,
    )
    if response.status != 200:
        raise ValueError(f"HTTP status {response.status}")
    return response


def run(config_path: Path, output: Path, allow_live: bool = False) -> int:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(config.get("sources"), list):
        raise ValueError("Config requires a sources list")
    candidates: list[dict] = []
    errors: list[dict] = []
    for source in config["sources"]:
        source_id = str(source.get("id", "unknown")) if isinstance(source, dict) else "invalid"
        try:
            validate_source(source)
            candidates.extend(extract(source, fetch_source(source, config_path.parent, allow_live)))
        except (ValueError, KeyError, TypeError, OSError) as exc:
            errors.append({"sourceId": source_id, "error": str(exc)})
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "candidates": candidates,
        "errors": errors,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Candidates: {len(candidates)}; source errors: {len(errors)}; output: {output}")
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract unapproved candidate deals using Scrapling")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-live", action="store_true", help="Opt into live permitted HTTP scraping")
    args = parser.parse_args()
    try:
        return run(args.config, args.output, args.allow_live)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
