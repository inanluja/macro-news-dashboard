import asyncio
from collections import OrderedDict
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sources import RSS_SOURCES
from fetcher import fetch_source

POLL_INTERVAL = 180  # seconds (3 minutes)
MAX_ARTICLES = 500   # keep last N articles in memory

app = FastAPI(title="News Fetcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store: id -> article dict (OrderedDict keeps insertion order)
_store: OrderedDict[str, dict] = OrderedDict()
_last_updated: str = ""
_is_fetching: bool = False


def _merge(new_articles: list[dict]):
    for article in new_articles:
        _store[article["id"]] = article

    # Trim to MAX_ARTICLES, keeping newest
    while len(_store) > MAX_ARTICLES:
        _store.popitem(last=False)


async def _poll():
    global _last_updated, _is_fetching
    while True:
        _is_fetching = True
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, fetch_source, src)
            for src in RSS_SOURCES
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                _merge(result)

        _last_updated = datetime.now(timezone.utc).isoformat()
        _is_fetching = False
        await asyncio.sleep(POLL_INTERVAL)


@app.on_event("startup")
async def startup():
    asyncio.create_task(_poll())


@app.get("/api/news")
def get_news(
    impact: str = None,
    category: str = None,
    tag: str = None,
    search: str = None,
    limit: int = 200,
):
    articles = list(_store.values())

    if impact:
        articles = [a for a in articles if a["impact"] == impact]
    if category:
        articles = [a for a in articles if a["category"] == category]
    if tag:
        articles = [a for a in articles if tag in a["tags"]]
    if search:
        q = search.lower()
        articles = [a for a in articles if q in a["title"].lower() or q in a["summary"].lower()]

    # Sort newest first
    articles.sort(key=lambda a: a["published"], reverse=True)
    return {
        "articles": articles[:limit],
        "total": len(articles),
        "last_updated": _last_updated,
        "is_fetching": _is_fetching,
    }


@app.get("/api/stats")
def get_stats():
    articles = list(_store.values())
    impact_counts = {}
    category_counts = {}
    tag_counts = {}

    for a in articles:
        impact_counts[a["impact"]] = impact_counts.get(a["impact"], 0) + 1
        category_counts[a["category"]] = category_counts.get(a["category"], 0) + 1
        for t in a["tags"]:
            tag_counts[t] = tag_counts.get(t, 0) + 1

    return {
        "total": len(articles),
        "by_impact": impact_counts,
        "by_category": category_counts,
        "top_tags": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        "last_updated": _last_updated,
    }
