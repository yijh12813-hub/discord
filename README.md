# Discord 中港美会计/财经信息聚合

## 第一步:在 Discord 创建服务器和频道
1. 打开 Discord → 左侧 `+` → "亲自创建" → 起个名字,例如 `会计财经聚合`
2. 创建 3 个文字频道: `实时快讯`、`每日报告`、`每周报告`

## 第二步:为每个频道创建 Webhook
对每个频道分别执行:
1. 点频道名旁边的齿轮图标(编辑频道)
2. 左侧选 "整合(Integrations)"
3. 点 "创建 Webhook"
4. 可以改名字/头像(可选),点 "复制 Webhook URL"

3 个频道各拿到一个 URL 后,把它们发给我,我会帮你写入 `webhooks.json`(格式见 `webhooks.example.json`)。

## 第三步:安装依赖(已完成)
```
pip3 install --user feedparser requests
```

## 脚本说明
- `python3 fetch.py` — 抓取所有源的新条目,写入 `data/YYYY-MM-DD.json`,不发送 Discord(用于测试)
- `python3 post_discord.py` — 抓取新条目 + 推送到 `#实时快讯`
- `python3 daily_report.py [YYYY-MM-DD]` — 打印当天原始条目(按地区分组),供撰写日报分析用
- `python3 weekly_report.py [YYYY-MM-DD]` — 打印过去 7 天原始条目(按地区分组),供撰写周报分析用
- `python3 post_report.py daily "正文"` / `post_report.py weekly "正文"` — 把写好的报告文字发到对应频道

## 调度
不需要用户自己开机器/写 cron。由 Claude 的定时例行任务负责:
1. 每小时跑一次 `post_discord.py`(准实时推送)
2. 每天 08:00 (HKT) 跑一次:读取 `daily_report.py` 的输出,由 Claude 撰写中文分析(中国大陆/香港/美国三段 + 当日要点),再用 `post_report.py daily` 发出
3. 每周一 08:00 (HKT) 跑一次:同理用 `weekly_report.py` 的输出生成周报

## 已知限制
- 彭博、财新、华尔街日报正文均为付费墙,聚合的是标题+摘要+链接,不含全文
- "实时"是轮询(默认每小时),不是真推送
- 会计准则相关新闻通过 Google News 关键词过滤(FASB / HKICPA / 企业会计准则等),覆盖面取决于 Google News 索引
