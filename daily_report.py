"""汇总当天抓取到的原始条目,按地区分组输出,供后续生成分析报告使用。
本脚本不做 AI 分析——分析由驱动它的 Claude 例行任务在读取这份汇总后自行撰写,
再调用 post_report.py 发送到 Discord,这样不需要额外的模型 API Key。
"""
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def load_day(date_str: str) -> list[dict]:
    log_file = DATA_DIR / f"{date_str}.json"
    if not log_file.exists():
        return []
    return json.loads(log_file.read_text())


def group_by_region(items: list[dict]) -> dict:
    grouped = defaultdict(list)
    for it in items:
        grouped[it["region"]].append(it)
    return grouped


if __name__ == "__main__":
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    items = load_day(date_str)
    grouped = group_by_region(items)

    print(f"=== {date_str} 原始条目汇总(共 {len(items)} 条)===\n")
    for region, entries in grouped.items():
        print(f"--- {region} ({len(entries)} 条) ---")
        for it in entries:
            print(f"  · {it['title']}  [{it['source']}]")
            print(f"    {it['url']}")
        print()
