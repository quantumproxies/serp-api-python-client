"""A small SERP API client: retries, pagination, CSV export, CLI.

    python3 -m serp_client "web scraping api" --country us --num 30 --csv out.csv
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Iterator

import requests

BASE = "https://api.quanticdata.io/v1"
RETRYABLE = {429, 500, 502, 503, 504}


@dataclass
class SerpClient:
    api_key: str = field(default_factory=lambda: os.environ.get("QUANTICDATA_API_KEY", ""))
    timeout: int = 120
    max_retries: int = 3

    def __post_init__(self) -> None:
        if not self.api_key:
            raise SystemExit("set QUANTICDATA_API_KEY — https://app.quanticdata.io/register")
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def search(self, query: str, **params: Any) -> dict:
        """One SERP call. Retries the transient statuses with exponential backoff."""
        body = {"query": query, **params}
        delay = 1.0
        for attempt in range(1, self.max_retries + 1):
            r = self._session.post(f"{BASE}/serp", json=body, timeout=self.timeout)
            if r.status_code in RETRYABLE and attempt < self.max_retries:
                time.sleep(delay)
                delay *= 2
                continue
            data = r.json()
            if data.get("type") == "error" or not r.ok:
                raise RuntimeError(f"serp failed ({r.status_code}): {data.get('message')}")
            return data.get("payload", {})
        raise RuntimeError("serp: retries exhausted")

    def paginate(self, query: str, want: int, **params: Any) -> Iterator[dict]:
        """Walk result pages until `want` organic rows have been yielded."""
        seen: set[str] = set()
        page = 1
        while len(seen) < want:
            payload = self.search(query, page=page, num=min(100, want), **params)
            rows = payload.get("organic") or []
            if not rows:
                return
            for row in rows:
                link = row.get("link")
                if not link or link in seen:
                    continue
                seen.add(link)
                yield row
                if len(seen) >= want:
                    return
            if not payload.get("has_next"):
                return
            page += 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Query the QuanticData SERP API.")
    ap.add_argument("query")
    ap.add_argument("--engine", default="google", choices=["google", "bing", "duckduckgo", "yandex"])
    ap.add_argument("--country", default=None, help="ISO code, e.g. us")
    ap.add_argument("--lang", default=None)
    ap.add_argument("--location", default=None, help='e.g. "Milan, Italy"')
    ap.add_argument("--num", type=int, default=10)
    ap.add_argument("--csv", default=None, metavar="FILE")
    args = ap.parse_args(argv)

    params = {k: v for k, v in
              dict(engine=args.engine, country=args.country, lang=args.lang, location=args.location).items()
              if v}

    rows = list(SerpClient().paginate(args.query, args.num, **params))
    for row in rows:
        print(f"{row.get('position'):>3}. {row.get('title')}\n     {row.get('link')}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["position", "title", "link", "displayed_link", "snippet"])
            w.writeheader()
            for row in rows:
                w.writerow({k: row.get(k) for k in w.fieldnames})
        print(f"\nwrote {len(rows)} rows to {args.csv}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
