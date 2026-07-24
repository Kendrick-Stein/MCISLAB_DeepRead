---
title: News Index
tags: [index, news]
---

# News 专栏

非论文信息源（博客/媒体/公众号）的定期摘要，由 `news-digest` skill 产出。
信息源配置在 `Workbench/config/team-config.json`：博客/媒体走 `news.sources`（rss/web 两型），
**公众号走 `news.wechat`**（关注账号 + 中文关键词，底层爬搜狗微信搜索，见 `scripts/wechat_search/`）。
`daily-papers` 也会顺带检索公众号，把它们解读的论文反查 arXiv 入队精读。

## 期数

（由 news-digest 追加，格式：`- [[News/YYYY-MM-DD]] — 一句话亮点`）

- [[News/2026-07-14]] — 首期：NVIDIA 开源 Nemotron agent 训练数据栈（10T+ token，强调失败覆盖）；"physical AI" 营销语义辨析；搜狗公众号源限流
- [[News/2026-07-19]] — Thinking Machines 发布 975B/41B 开源多模态 MoE Inkling（含"模型自主微调自己"demo）；Sutton 离开 Keen 创立 Oak Lab 押注无重放 continual learning
- [[News/2026-07-24]] — Sonnet 5 把 OSWorld ≈78% 级 agentic 能力压到 $2/$10 定价；Fable 5 出口管制风波与 jailbreak 严重度共识框架；AllenAI Shippy 生产级 agent 工程复盘；LeRobot v0.6.0 world-model policy 进主流工具链
