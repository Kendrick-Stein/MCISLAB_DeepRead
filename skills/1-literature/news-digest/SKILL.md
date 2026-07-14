---
name: news-digest
description: >
  当 Supervisor 说"看看最近有什么 AI 新闻""news 总结"，或 autoresearch 检测到
  News/ 超期未更新时，抓取 config 中的博客/新闻/公众号源，按研究兴趣筛选点评，
  产出 News/YYYY-MM-DD.md 并把重要线索回链进 vault。
argument-hint: "[今日 / 过去N天，默认取 config news.days]"
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
---

## Purpose

非论文信息源（官方博客、技术媒体、公众号）的摄入端，架构与 daily-papers 相同的三段式：
脚本抓取打分（零 token）→ 分流 → 精读点评。产出周报式 News 摘要；真正有信息量的条目
（新工具/重要发布/研究 idea 线索）沉淀为可 wikilink 的小节回链进 survey/agenda，
让网络信息也进入知识复利循环。

## Steps

### Step 0：解析时间范围

"今日" → `--days 1`；"过去N天/一周" → 对应天数；未指定 → 省略参数（用 config news.days）。

### Step 1：抓取打分（零 token）

```bash
python3 skills/1-literature/news-digest/fetch_news.py --days {DAYS} \
  --output Workbench/daily/.news-candidates.json
```

Read 输出 JSON：`candidates`（RSS 已打分排序；`title_only: true` 的条目来自无摘要 feed，
脚本无从预筛而全量保留，分流时需自行判断相关性）、`web_sources`（需 agent 抓取的网页源）、
`errors`（失败源）。对每个 web_source 用 WebFetch（或 `scripts/lexmount_fetch.py` fallback，
见 references/network-fetch-fallback.md）抓首页，人工筛出时间范围内的条目并入候选。

**公众号源（若 config `news.wechat.enabled`）**：再跑一次微信搜索（爬搜狗，零 token）：

```bash
python3 scripts/wechat_search/fetch_wechat.py --days {DAYS} \
  --output Workbench/daily/.wechat-candidates.json
```

Read 输出 JSON：`candidates` 已按 `watched`（是否来自关注账号）+ 打分排序，字段与上面的
news candidates 对齐（title/link/summary/source/published/score），可直接并入候选池。
`errors` 记录被搜狗限流/失败的关键词。**首次运行**若报 `node_modules 缺失`，先
`cd scripts/wechat_search && npm install`（依赖 Node 18+ 与 cheerio）。搜狗返回的是中间链，
精读时若打不开可提示用户在浏览器打开或据标题+摘要判断。

### Step 2：分流

扫 title + summary，把候选分为：**精读**（与 interests 强相关、含新方法/新产品/新数据点，
通常 3-8 条）、**一句话带过**（相关但无增量）、**忽略**。

### Step 3：精读并产出

对精读条目用 WebFetch 读原文。产出 `News/YYYY-MM-DD.md`：

```markdown
---
title: "News {YYYY-MM-DD}"
tags: [news]
date: "{YYYY-MM-DD}"
sources_ok: {N}
sources_failed: [{失败源名}]
---

# News {YYYY-MM-DD}

## 精读

### {条目标题}
- **source**: [{源名}]({url})
- **what**: <发生了什么，2-3 句>
- **so-what**: <对我们研究方向的含义/态度，1-2 句；无关痛痒的不硬写>
- **action**: <无 / 建议 digest 论文 arXiv:xxxx / 关联 [[Topics/...]] 或 [[Ideas/...]]>

## 一句话

- [{标题}]({url}) — <一句话> （source）
```

### Step 4：回链与记录

1. action 中"建议 digest"的论文：追加 summarize_paper 任务到 `Workbench/queue.json`
   （最小结构：`{"task": {"task_id": "<8位hex>", "task_type": "summarize_paper", "title": "Summarize: <标题>", "goal": "Generate structured note for paper '<标题>'", "topic": null, "input_refs": ["<年份-标题>"], "output_path": null, "priority": 50, "status": "pending", "dependencies": [], "metadata": {"paper_url": "<arXiv url>"}}, "added_at": "<ISO 时间戳>", "source": "news-digest", "attempts": 0, "last_attempt": null}`——与 queue.json 现有条目结构一致）。
2. 更新 `News/_index.md` 期数列表：追加一行 `- [[News/YYYY-MM-DD]] — 一句话亮点`。
3. 与某 direction 强相关的条目：不改 `Workbench/agenda.md`（agenda 只由 agenda-evolve/
   Supervisor 改），仅在当日 log 中提示。
4. 追加当日 log：`### [HH:MM] news-digest — N 精读 / M 一句话 / K 源失败`。

## Guard

- News 条目是线索与观点来源，**不得作为 agenda evidence 的唯一支撑**（非 peer-reviewed）。
  公众号文章尤其如此——它多为二手解读，真正的证据是它指向的原始论文（应 digest 原文）。
- 抓取失败的源跳过并记入 frontmatter `sources_failed` 与当日 log，不阻塞。微信源被搜狗限流
  （`.wechat-candidates.json` 的 `errors` 非空或候选为 0）视同单源失败，跳过不阻塞。
- 不直接修改 agenda.md / Topics/（只回链与提示，改动走各自 owner skill）。
- so-what 必须诚实：没有含义就写"与当前方向无直接关联"，不硬编。

## Verify

- [ ] News/YYYY-MM-DD.md 存在且精读条目均有 source/what/so-what/action
- [ ] News/_index.md 已追加本期
- [ ] 建议 digest 的论文已入 queue.json
- [ ] 当日 log 已追加
