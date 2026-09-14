"""汇总过去 7 天的原始条目,按地区分组输出,供生成周报分析使用。用法同 daily_report.py。"""
import sys
from collections import defaultdict
from datetime import datetime, timedelta

from daily_report import load_day, group_by_region

if __name__ == "__main__":
    end_date = datetime.now()
    if len(sys.argv) > 1:
        end_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")

    all_items = []
    dates = []
    for i in range(7):
        d = end_date - timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        dates.append(date_str)
        all_items.extend(load_day(date_str))

    grouped = group_by_region(all_items)

    print(f"=== 周报原始条目汇总 {dates[-1]} ~ {dates[0]}(共 {len(all_items)} 条)===\n")
    for region, entries in grouped.items():
        print(f"--- {region} ({len(entries)} 条) ---")
        for it in entries:
            print(f"  · {it['title']}  [{it['source']} / {it.get('published', '')}]")
            print(f"    {it['url']}")
        print()
