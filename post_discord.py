"""把新条目格式化为 Discord Embed 并发送到 #实时快讯 Webhook。"""
import time

import requests

from config import load_webhooks
from fetch import fetch_new_entries, append_to_daily_log

REGION_COLOR = {
    "中国大陆": 0xE63946,
    "香港": 0x2A9D8F,
    "美国": 0x1D3557,
    "综合": 0x6C757D,
}

MAX_EMBEDS_PER_MESSAGE = 10


def build_embed(item: dict) -> dict:
    return {
        "title": item["title"][:250],
        "url": item["url"],
        "description": item["summary"],
        "color": REGION_COLOR.get(item["region"], 0x6C757D),
        "footer": {"text": f"{item['region']} · {item['source']}"},
    }


def post_items(webhook_url: str, items: list[dict]) -> None:
    for i in range(0, len(items), MAX_EMBEDS_PER_MESSAGE):
        batch = items[i : i + MAX_EMBEDS_PER_MESSAGE]
        payload = {"embeds": [build_embed(it) for it in batch]}
        for attempt in range(3):
            try:
                resp = requests.post(webhook_url, json=payload, timeout=20)
                if resp.status_code >= 300:
                    print(f"[warn] Discord 推送失败 {resp.status_code}: {resp.text}")
                break
            except requests.exceptions.RequestException as e:
                print(f"[warn] 网络错误,重试 {attempt + 1}/3: {e}")
                time.sleep(3)
        time.sleep(1)  # 避免触发 Discord rate limit


if __name__ == "__main__":
    webhooks = load_webhooks()
    new_items = fetch_new_entries()
    append_to_daily_log(new_items)

    if not new_items:
        print("没有新内容")
    else:
        post_items(webhooks["realtime"], new_items)
        print(f"已推送 {len(new_items)} 条新内容到 #实时快讯")
