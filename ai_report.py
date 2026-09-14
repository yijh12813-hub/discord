"""调用 Anthropic API,把当天/当周原始条目写成中文分析报告并发到 Discord。
用法: python3 ai_report.py daily
      python3 ai_report.py weekly
需要环境变量 ANTHROPIC_API_KEY。
"""
import os
import sys
from datetime import datetime

import requests

from daily_report import load_day, format_items
from weekly_report import load_past_week
from post_report import post_report

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = "claude-sonnet-4-6"

DAILY_INSTRUCTIONS = """你是一名财经分析师,请基于下面这些当天抓取到的原始新闻标题(来自中国大陆、香港、美国三地的财经媒体与 Google News 过滤源),撰写一段结构化中文日报分析,要求:
- 开头标注日期和当日总条目数
- 分 🇨🇳 中国大陆 / 🇭🇰 香港 / 🇺🇸 美国 三个部分,每部分 2-5 条要点,优先选择会计准则变化、监管动态、重大市场事件,不要机械罗列每条标题,要提炼和综合
- 结尾加一段「要点提炼」,找出三地共同或关联的趋势/信号
- 总长度控制在 3500 字以内
- 如果某个地区当天没有有价值的内容,如实说明,不要编造

原始条目:
{items}
"""

WEEKLY_INSTRUCTIONS = """你是一名财经分析师,请基于下面这些过去 7 天抓取到的原始新闻标题(来自中国大陆、香港、美国三地的财经媒体与 Google News 过滤源),撰写一段结构化中文周报分析,要求:
- 开头标注周报时间范围和总条目数
- 分 🇨🇳 中国大陆 / 🇭🇰 香港 / 🇺🇸 美国 三个部分,每部分总结本周最重要的 3-6 个事件/趋势(优先会计准则变化、监管政策、重大市场事件),要有趋势性判断而不是流水账式罗列
- 结尾加一段「本周重点回顾与下周关注」,给出值得持续跟进的话题
- 总长度控制在 4500 字以内
- 如果某个地区本周没有特别有价值的内容,如实说明,不要编造

原始条目:
{items}
"""


def call_claude(prompt: str) -> str:
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": ANTHROPIC_MODEL,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return "".join(block["text"] for block in data["content"] if block["type"] == "text")


def generate_daily() -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    items = load_day(date_str)
    if not items:
        return f"📊 中港美会计与财经日报 · {date_str}\n\n今天没有抓取到新条目,可能是抓取任务尚未运行或当天确实无更新。"
    raw_text = format_items(items, date_str)
    return call_claude(DAILY_INSTRUCTIONS.format(items=raw_text))


def generate_weekly() -> str:
    end_date = datetime.now()
    items, dates = load_past_week(end_date)
    if not items:
        return f"📊 中港美会计与财经周报 · {dates[-1]} ~ {dates[0]}\n\n本周没有抓取到任何条目。"
    raw_text = format_items(items, f"{dates[-1]} ~ {dates[0]}")
    return call_claude(WEEKLY_INSTRUCTIONS.format(items=raw_text))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("daily", "weekly"):
        print("用法: python3 ai_report.py <daily|weekly>")
        sys.exit(1)
    if not ANTHROPIC_API_KEY:
        print("[error] 未设置环境变量 ANTHROPIC_API_KEY")
        sys.exit(1)

    kind = sys.argv[1]
    report_text = generate_daily() if kind == "daily" else generate_weekly()
    post_report(kind, report_text)
    print(f"{kind} 报告已生成并发送,长度 {len(report_text)} 字")
