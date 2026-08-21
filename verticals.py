"""One call per vertical — what each `search_type` gives you back.

Verticals are not all keyed by a query: place_details wants a place_id/data_id,
product wants a product_id, flights wants airport codes and dates. The ones below
are the query-driven ones you can run straight away.
"""
from serp_client import SerpClient

client = SerpClient()

CASES = [
    ("search", {"query": "residential proxies", "country": "us"}, "organic"),
    ("news", {"query": "web scraping lawsuit", "country": "us"}, "news"),
    ("shopping", {"query": "nike pegasus 41", "country": "us"}, "shopping"),
    ("images", {"query": "proxy server diagram", "country": "us"}, "images"),
    ("videos", {"query": "playwright tutorial", "country": "us"}, "videos"),
    ("places", {"query": "coffee roasters", "location": "Milan, Italy"}, "places"),
    ("jobs", {"query": "data engineer", "location": "Berlin, Germany"}, "jobs"),
    ("scholar", {"query": "web crawling ethics", "country": "us"}, "organic"),
    ("autocomplete", {"query": "how to scrape "}, "suggestions"),
]

for search_type, params, key in CASES:
    query = params.pop("query")
    try:
        payload = client.search(query, search_type=search_type, **params)
    except RuntimeError as exc:
        print(f"{search_type:<13} !! {exc}")
        continue
    rows = payload.get(key) or []
    first = rows[0] if rows else {}
    label = first.get("title") or first.get("value") or first.get("name") or "-"
    print(f"{search_type:<13} {len(rows):>3} rows   first: {str(label)[:60]}")
