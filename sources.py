"""信息源定义。每个源标注所属地区,便于日报/周报按地区分类。"""

REGION_CN = "中国大陆"
REGION_HK = "香港"
REGION_US = "美国"
REGION_GLOBAL = "综合"

GOOGLE_NEWS_TEMPLATE = "https://news.google.com/rss/search?q={query}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"


def _google_news(query: str) -> str:
    from urllib.parse import quote
    return GOOGLE_NEWS_TEMPLATE.format(query=quote(query))


SOURCES = [
    # 官方直接 RSS
    {
        "name": "WSJ Markets",
        "region": REGION_US,
        "url": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    },
    {
        "name": "Bloomberg Green",
        "region": REGION_GLOBAL,
        "url": "https://feeds.bloomberg.com/green/news.rss",
    },
    # Google News 按来源/关键词过滤,覆盖官方无公开 RSS 的部分
    {
        "name": "Bloomberg (Google News)",
        "region": REGION_GLOBAL,
        "url": _google_news("site:bloomberg.com/news"),
    },
    {
        "name": "WSJ 中文 (Google News)",
        "region": REGION_US,
        "url": _google_news("site:cn.wsj.com"),
    },
    {
        "name": "财新 (Google News)",
        "region": REGION_CN,
        "url": _google_news("caixin.com 财经 OR 公司 OR 市场 OR 监管"),
    },
    {
        "name": "中国会计准则 (Google News)",
        "region": REGION_CN,
        "url": _google_news("企业会计准则 OR 财政部会计司 OR 中国证监会 会计"),
    },
    {
        "name": "香港会计与市场 (Google News)",
        "region": REGION_HK,
        "url": _google_news("HKICPA OR 香港会计师公会 OR 港交所 财报 OR HKEX disclosure"),
    },
    {
        "name": "美国会计准则 (Google News)",
        "region": REGION_US,
        "url": _google_news("FASB OR \"accounting standards update\" OR SEC accounting rule"),
    },
]
