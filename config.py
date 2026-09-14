"""Webhook 配置。首次使用前请复制 webhooks.example.json 为 webhooks.json 并填入真实 URL。"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "webhooks.json"


def load_webhooks() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"未找到 {CONFIG_FILE}。请复制 webhooks.example.json 为 webhooks.json 并填入 Discord Webhook URL。"
        )
    return json.loads(CONFIG_FILE.read_text())
