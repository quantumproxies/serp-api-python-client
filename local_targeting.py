"""The same keyword from ten cities — local rank is not national rank.

`location` takes a human-readable place and is encoded to a uule token server-side,
so the engine answers as if the searcher were standing there. Pass `uule` yourself
(token, or raw "lat,lon[,radius]") when you need coordinates instead of a city name.
"""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from serp_client import SerpClient

QUERY = "emergency plumber"
CITIES = [
    "New York, New York, United States",
    "Los Angeles, California, United States",
    "Chicago, Illinois, United States",
    "Houston, Texas, United States",
    "Phoenix, Arizona, United States",
    "Philadelphia, Pennsylvania, United States",
    "San Antonio, Texas, United States",
    "San Diego, California, United States",
    "Dallas, Texas, United States",
    "Austin, Texas, United States",
]

client = SerpClient()


def ranks(city: str) -> tuple[str, dict[str, int]]:
    payload = client.search(QUERY, country="us", lang="en", location=city, num=20)
    return city, {row["link"]: row["position"] for row in payload.get("organic", []) if row.get("link")}


by_domain: dict[str, dict[str, int]] = defaultdict(dict)
with ThreadPoolExecutor(max_workers=5) as pool:
    for city, mapping in pool.map(ranks, CITIES):
        for link, position in mapping.items():
            host = link.split("/")[2] if "://" in link else link
            by_domain[host].setdefault(city, position)

# Domains that rank in the most cities, i.e. the ones with real local coverage.
ranked = sorted(by_domain.items(), key=lambda kv: (-len(kv[1]), min(kv[1].values())))
for host, cities in ranked[:15]:
    avg = sum(cities.values()) / len(cities)
    print(f"{host:<40} {len(cities):>2}/{len(CITIES)} cities   avg rank {avg:4.1f}")
