# SERP API in Python — Google, Bing, DuckDuckGo and Yandex as JSON

A small, dependency-light client for the [QuanticData SERP API](https://quanticdata.io/serp-api/):
one `POST /v1/serp` returns parsed search results — organic rows with position, title, link,
displayed link, snippet and sitelinks, plus the local pack, news, videos, shopping, images,
ads and related searches when the page carries them.

Four engines, **eighteen verticals**, per-country and per-city targeting. From $0.0005 a search.

```bash
pip install requests
export QUANTICDATA_API_KEY=qd_live_your_key_here
python3 -m serp_client "web scraping api" --country us --num 20
```

## Files

| File | What it is |
|---|---|
| [`serp_client.py`](serp_client.py) | the client: retries, pagination, CLI, CSV output |
| [`verticals.py`](verticals.py) | one call per vertical — news, shopping, images, videos, places, jobs, scholar, autocomplete |
| [`local_targeting.py`](local_targeting.py) | the same query from ten cities via `location`, with rank deltas |

## Request fields

| Field | Values |
|---|---|
| `query` | the search string (optional for id-addressed verticals) |
| `engine` | `google` (default), `bing`, `duckduckgo`, `yandex` |
| `search_type` | `search`, `shopping`, `images`, `news`, `places`, `maps`, `videos`, `scholar`, `jobs`, `autocomplete`, `place_details`, `hotels`, `flights`, `events`, `product`, `lens`, `reviews`, `trends` |
| `country` | ISO code — sets both the proxy exit and the engine locale (`gl`) |
| `lang` | interface language (`hl`), e.g. `en`, `it` |
| `num` | 1–100, default 10 |
| `page` | 1-based result page |
| `location` | human-readable place, e.g. `"Milan, Italy"` — encoded to `uule` for you |
| `uule` | a `uule` token, or raw `lat,lon[,radius]` |
| `render` | force JS rendering (on by default for Google and Yandex) |

## Response

```jsonc
{
  "type": "response",
  "payload": {
    "organic": [
      { "position": 1, "title": "…", "link": "https://…",
        "displayed_link": "example.com › docs", "snippet": "…", "sitelinks": [] }
    ],
    "related_searches": ["…"],
    "results_count": 1230000,
    "has_next": true,
    "search_metadata": { "query": "…", "engine": "google" },
    "usage": { "cost_usd": 0.0005 }
  }
}
```

Empty `organic` with `results_count: 0` is a genuinely empty SERP, not a block — blocks come
back as an error, and errors are not billed.

## Related

- [How a SERP API works](https://quanticdata.io/blog/how-a-serp-api-works/)
- [How to use a SERP API](https://quanticdata.io/blog/how-to-use-a-serp-api/) · [How to create a SERP API key](https://quanticdata.io/blog/how-to-create-a-serp-api-key/)
- [Google Search Results collector](https://quanticdata.io/collectors/google-search-results-api/) — the same data, paginated and billed per row
- [Keyword research API](https://quanticdata.io/collectors/keyword-research-api/)

## Node.js

The minimal call without Python: Node 18 or newer, no dependencies. See [`serp.mjs`](serp.mjs):

```bash
export QUANTICDATA_API_KEY=qd_live_your_key_here
node serp.mjs "best coffee grinder" us
```

## Sample response

A real `POST /v1/serp` call from 4 October 2026: `best coffee grinder`, Google, United States. One organic row is shown here; the trimmed payload is in [`sample-response.json`](sample-response.json).

```json
{
  "rank": 3,
  "title": "The 9 Best Coffee Grinders of 2026, Tested & Reviewed - Serious Eats",
  "link": "https://www.seriouseats.com/the-best-coffee-grinders",
  "display_link": "www.seriouseats.com › Equipment › Coffee & Tea › Gear",
  "source": "seriouseats.com",
  "description": "The Baratza Virtuoso+ is the best coffee grinder for the bean-obsessed. With over 40 settings, it offers versatility without being over-designed ...",
  "sitelinks": [
    {
      "title": "Top Picks",
      "link": "https://www.seriouseats.com/the-best-coffee-grinders#toc-top-picks"
    },
    {
      "title": "The Tests",
      "link": "https://www.seriouseats.com/the-best-coffee-grinders#toc-the-tests"
    }
  ]
}
```

MIT licensed.
