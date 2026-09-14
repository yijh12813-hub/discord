# Discord 中港美会计/财经信息聚合

## 架构说明

之前尝试过用 Claude 云端定时任务(remote routine)跑抓取+推送,诊断发现那个沙盒环境的出站代理只放行 GitHub/pip,访问不了任何新闻网站也访问不了 Discord。所以最终方案改成全部用 **GitHub Actions**:

- `.github/workflows/realtime.yml` —— 每小时跑一次 `fetch.py` + `post_discord.py`,抓新内容推到 `#实时快讯`
- `.github/workflows/daily.yml` —— 每天 UTC 00:00(香港/上海时间 08:00)调用 Anthropic API 生成中文日报,发到 `#每日报告`
- `.github/workflows/weekly.yml` —— 每周一同一时间生成周报,发到 `#每周报告`

每次运行后,Actions 会把更新后的 `state.json`(去重状态)和 `data/*.json`(当天抓到的条目)提交回仓库,供下一次运行读取。

## 需要你配置的东西

去仓库页面 → **Settings → Secrets and variables → Actions → New repository secret**,添加 4 个 secret:

| Secret 名 | 值 |
|---|---|
| `DISCORD_WEBHOOK_REALTIME` | 实时快讯频道的 Webhook URL |
| `DISCORD_WEBHOOK_DAILY` | 每日报告频道的 Webhook URL |
| `DISCORD_WEBHOOK_WEEKLY` | 每周报告频道的 Webhook URL |
| `ANTHROPIC_API_KEY` | 去 https://console.anthropic.com 创建账号并生成的 API Key |

Secrets 只有 Actions 运行时能读到,不会出现在代码或日志里。

## 本地脚本说明(手动测试用)

- `python3 fetch.py` —— 抓取新条目写入 `data/`,不发 Discord
- `python3 post_discord.py` —— 抓取 + 推送到 `#实时快讯`
- `python3 ai_report.py daily` / `ai_report.py weekly` —— 需要本地设置 `ANTHROPIC_API_KEY` 环境变量,调用 API 生成报告并发送
- `python3 post_report.py daily "文本"` —— 直接发一段已经写好的文字到指定频道

## 已知限制

- 彭博、财新、华尔街日报正文均为付费墙,聚合的是标题+摘要+链接,不含全文
- "实时"是每小时轮询,不是真推送
- 会计准则相关新闻通过 Google News 关键词过滤(FASB / HKICPA / 企业会计准则等)
- Anthropic API 会产生少量调用费用(用 Sonnet 模型,每天日报+周报加起来预计几美分到一毛钱左右)
