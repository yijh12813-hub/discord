"""抓取 sources.py 中定义的所有源,去重后返回/落盘新条目。"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import feedparser

from sources import SOURCES

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
STATE_FILE = BASE_DIR / "state.json"

DATA_DIR.mkdir(exist_ok=True)


def load_state() -> set:
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()


def save_state(seen_urls: set) -> None:
    STATE_FILE.write_text(json.dumps(sorted(seen_urls), ensure_ascii=False, indent=2))


def fetch_new_entries() -> list[dict]:
    seen = load_state()
    new_items = []

    for source in SOURCES:
        try:
            feed = feedparser.parse(source["url"])
        except Exception as e:
            print(f"[warn] 抓取失败 {source['name']}: {e}")
            continue

        for entry in feed.entries[:30]:
            url = entry.get("link", "")
            if not url or url in seen:
                continue

            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()
            if len(summary) > 300:
                summary = summary[:300] + "..."

            published = entry.get("published", "") or entry.get("updated", "")

            item = {
                "title": title,
                "summary": summary,
                "url": url,
                "source": source["name"],
                "region": source["region"],
                "published": published,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            new_items.append(item)
            seen.add(url)

    save_state(seen)
    return new_items


def append_to_daily_log(items: list[dict]) -> None:
    if not items:
        return
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = DATA_DIR / f"{today}.json"
    existing = json.loads(log_file.read_text()) if log_file.exists() else []
    existing.extend(items)
    log_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    new_items = fetch_new_entries()
    append_to_daily_log(new_items)
    print(f"抓到 {len(new_items)} 条新内容")
    for it in new_items:
        print(f"  [{it['region']}] {it['source']}: {it['title']}")
