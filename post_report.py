"""把已经写好的日报/周报文本发送到对应 Discord Webhook。
用法: python3 post_report.py daily "报告正文..."
      python3 post_report.py weekly "报告正文..."
正文过长时(Discord 单条消息上限 2000 字符)自动分段发送。
"""
import sys
import time

import requests

from config import load_webhooks

CHUNK_SIZE = 1900


def chunk_text(text: str) -> list[str]:
    chunks = []
    while text:
        chunks.append(text[:CHUNK_SIZE])
        text = text[CHUNK_SIZE:]
    return chunks


def post_report(kind: str, content: str) -> None:
    webhooks = load_webhooks()
    if kind not in ("daily", "weekly"):
        raise ValueError("kind 必须是 daily 或 weekly")

    url = webhooks[kind]
    for chunk in chunk_text(content):
        for attempt in range(3):
            try:
                resp = requests.post(url, json={"content": chunk}, timeout=20)
                if resp.status_code >= 300:
                    print(f"[warn] Discord 推送失败 {resp.status_code}: {resp.text}")
                break
            except requests.exceptions.RequestException as e:
                print(f"[warn] 网络错误,重试 {attempt + 1}/3: {e}")
                time.sleep(3)
        time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 post_report.py <daily|weekly> \"报告正文\"")
        sys.exit(1)
    post_report(sys.argv[1], sys.argv[2])
