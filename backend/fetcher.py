import feedparser
import hashlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from classifier import classify

TIMEOUT = 10


def _parse_date(entry) -> datetime:
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                return parsedate_to_datetime(raw).astimezone(timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def _entry_id(entry, source_name: str) -> str:
    raw = getattr(entry, "id", None) or getattr(entry, "link", None) or (source_name + entry.get("title", ""))
    return hashlib.md5(raw.encode()).hexdigest()


def fetch_source(source: dict) -> list[dict]:
    try:
        feed = feedparser.parse(source["url"], request_headers={"User-Agent": "Mozilla/5.0"})
    except Exception:
        return []

    articles = []
    for entry in feed.entries[:15]:  # latest 15 per source
        title = getattr(entry, "title", "").strip()
        summary = getattr(entry, "summary", "").strip()
        # strip HTML tags from summary
        summary = re.sub(r"<[^>]+>", "", summary) if summary else ""
        link = getattr(entry, "link", "")
        pub = _parse_date(entry)
        classification = classify(title, summary)

        articles.append({
            "id": _entry_id(entry, source["name"]),
            "source": source["name"],
            "category": source["category"],
            "title": title,
            "summary": summary[:400] if summary else "",
            "link": link,
            "published": pub.isoformat(),
            "tags": classification["tags"],
            "impact": classification["impact"],
        })
    return articles


# needed for strip inside fetch_source
import re
