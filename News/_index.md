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
