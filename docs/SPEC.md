# ReadPaperMachine Specification

> 本文件是 ReadPaperMachine 的 single source of truth。

**Last updated**: 2026-07-06（skill 通过 repo 内 `.claude/skills/` 符号链接自动注册，见 §1 Setup）

---

## 1. What is ReadPaperMachine

ReadPaperMachine 是一个基于 Obsidian 的 **AI-assisted 科研知识管理系统**。它将论文阅读、idea 孵化、实验追踪、记忆蒸馏等科研工作流编码为可执行的 Markdown skill，在 vault 内直接执行。

设计灵感来自 [MindFlow](https://github.com/liqing-ustc/mindflow)。

### 角色定位

- **Researcher（AI）**：有自己的研究议程，独立驱动日常工作——读论文、跑实验、写初稿、调整方向
- **Supervisor（Human）**：设定高层研究方向，定期 check-in，给战略性建议

### 设计哲学

```
Insight  — 目标不是论文数量，而是 "我们理解了什么新东西？"
Trust    — 透明 → 可审计 → 信任
Markdown — 一切皆文件，一切可读，一切有版本控制
```

### Setup

Skill 通过 repo 内 `.claude/skills/` 符号链接指向 `skills/<category>/<name>/` 自动注册给 Claude Code；
`python3 scripts/sync_skills.py --fix` 校验并修复缺失/失效的链接。新环境用 `bash scripts/init.sh`
（加 `--fresh` 可清空示例论文/idea，走向导设置研究方向与关键词）完成一次性初始化。

## 2. Architecture

```
┌─────────────────────────────────────────────────┐
│  AI Agent (Claude / Gemini)                     │
│  Reads SKILL.md → Reads/Writes vault Markdown   │
├─────────────────────────────────────────────────┤
│  Skill Protocol (skills/*/SKILL.md)              │
│  Zero dependency, any agent can execute          │
├─────────────────────────────────────────────────┤
│  Obsidian Vault (Markdown)                       │
│  Papers/ Topics/ Ideas/ DomainMaps/              │
│  Workbench/ (Researcher working state)           │
└─────────────────────────────────────────────────┘
```

## 3. Directory Structure

```
ReadPaperMachine/
├── Papers/              # 论文笔记（YYMM-ShortTitle.md，Archive/ 存放被取代/降级的笔记）
├── Ideas/               # 研究 idea
├── Experiments/         # 实验记录（YYYY-MM-DD-Name.md）
├── Projects/            # 项目追踪
├── Topics/              # 文献调研 / 跨论文分析报告
├── Reports/             # 生成的报告
├── News/                # 非论文信息源摘要（news-digest 产出）
├── Meetings/            # 会议记录
│
├── DomainMaps/          # 核心认知地图（survey-refresh 自动维护"近期格局变化"；结构性内容经 queue Review 由 Human 晋升）
│   ├── _index.md        #   索引页
│   └── {Name}.md        #   各 domain 认知地图
│
├── Templates/           # Obsidian 模板
│
├── skills/              # Skill 定义
│   ├── 1-literature/    #   文献技能
│   ├── 2-ideation/      #   创意技能
│   ├── 3-experiment/    #   实验技能
│   ├── 4-writing/       #   写作技能
│   ├── 5-evolution/     #   进化技能
│   ├── 6-orchestration/ #   编排技能
│   └── 7-presentation/  #   展示技能
│
├── references/          # 协议文档
│   ├── skill-protocol.md
│   ├── memory-protocol.md
│   ├── agenda-protocol.md
│   └── tags.md
│
├── Workbench/           # Researcher 工作状态
│   ├── agenda.md        #   研究议程
│   ├── memory/          #   蒸馏后的记忆
│   ├── queue.md         #   待办队列
│   ├── logs/            #   每日操作日志
│   ├── survey-updates.json  # digest→survey 记账（paper-digest 写，survey-refresh 消费）
│   └── evolution/       #   演化记录
│
├── docs/SPEC.md         # 本文件
└── AGENTS.md            # Researcher 身份与操作指令
```

## 4. Skill List

| Category | Skill | 功能 |
|:---------|:------|:-----|
| `1-literature` | `paper-digest` | 消化单篇论文 → Paper 笔记 |
| | `literature-survey` | 主题级调研（搜索 + 批量 digest + 综合） |
| | `daily-papers` | 抓取 HF Daily/Trending + arXiv，打分筛选 + 锐评 |
| | `survey-refresh` | 把 digest 积压的新论文增量并入 survey + 刷新 DomainMap |
| | `news-digest` | 非论文信息源（RSS/Atom 等）摘要 → News/ |
| `2-ideation` | `idea-generate` | 从知识空白生成研究 idea |
| | `idea-evaluate` | 评估 idea 可行性和新颖性 |
| `3-experiment` | `experiment-design` | 设计实验方案 |
| | `experiment-track` | 记录实验进展和结果 |
| | `result-analysis` | 分析实验结果，提取 insight |
| `4-writing` | `draft-section` | 起草论文/报告章节 |
| | `writing-refine` | 打磨已有文稿 |
| | `latex-citation-enhancer` | 固化 cite_key + 抓权威 BibTeX → 生成 references.bib |
| | `auto-cite` | 给 LaTeX 草稿逐条判断 + 确认后插入 `\cite{}`（基于 Papers/） |
| | `related-work` | 起草英文 LaTeX Related Work 章节 |
| `5-evolution` | `memory-distill` | 从日志蒸馏记忆 |
| | `agenda-evolve` | 演化研究议程 |
| | `memory-retrieve` | 从记忆库检索相关经验 |
| `6-orchestration` | `autoresearch` | 核心研究循环 |
| | `research-team` | 多 Agent 并行协作构建知识库 |
| `7-presentation` | `domain-presentation` | Domain Map → HTML 可视化展示 |

## 5. Conventions

> 这些约定用于防止 vault 随产出增长而失序。新建/移动文件时遵守。

### 5.1 Papers 命名

- 规范文件名：`YYMM-ShortTitle.md`，`YY`=年份后两位、`MM`=arXiv/发表月份（如 2026-04 → `2604`）。
- 月份未知时用 `00` 占位（如 `2500` = 2025 年月份未知）。**不要**用 4 位年份（`2025-`/`2026-`）作前缀——这是历史遗留写法，新笔记一律用 `YYMM`。
- `ShortTitle` 用 PascalCase，去掉冒号/空格（`AutoGUI-v2` → `AutoGUIv2`）。

### 5.2 Papers/Archive 策略

- `Papers/` 根目录 = **当前 active focus** 的笔记，是每篇论文的**唯一 canonical 位置**。
- `Papers/Archive/` = 已 digest 但**偏离当前研究重心**、或被更完整笔记取代的论文。
- **不变量**：同一文件名不得同时存在于 `Papers/` 和 `Papers/Archive/`。re-digest 产生更完整版本时，保留 root 版、删除 Archive stub（历史可经 git 找回）。
- 被 agenda/idea 作为 active evidence 引用的论文应放在 `Papers/` 根目录。

### 5.3 Reports vs Topics

- `Topics/` = **沉淀性**跨论文调研（`*-Survey.md`），与某个 DomainMap 长期对应，会被持续更新。
- `Reports/` = **某一时点**生成的报告/提案（`YYYY-MM-DD-Name.md`）。其中 autoresearch 的周期性 pulse/update 属临时产物，可定期清理或归入子目录。

### 5.4 Wikilink 风格

- 引用论文优先用**纯文件名** `[[2604-GoClick]]`（Obsidian 按文件名解析，不受 Papers/ 还是 Papers/Archive/ 影响），避免写死路径 `[[Papers/2604-GoClick]]`（移动文件即断链）。
- 文件名含空格/冒号会导致 wikilink 解析失败——引用前确认目标文件名符合 5.1。

### 5.5 引用身份 frontmatter（cite_key / arxiv_id / doi）

- 每篇 `Papers/*.md` 在 digest 时固化三个引用身份字段：
  - `arxiv_id`：如 `"2606.19409"`（非 arXiv 留空），由 `assign_cite_keys.py` 从 url 自动抽取。
  - `doi`：期刊/会议 DOI（有则填）。
  - `cite_key`：LaTeX 引用 key，格式 `{lastname}{year}{firstTitleWord}`（如 `wen2026openrath`）。
- **不变量**：`cite_key` 一旦写入**永久冻结**——保证已发草稿里的 `\cite{}` 永不失效。改 key 须手动编辑该字段；工具（`assign_cite_keys.py`）只为缺失的论文分配、绝不覆盖。
- 权威 BibTeX 缓存在 `references/bibtex-cache.bib`（按 cite_key 索引，`source=arxiv|crossref|reconstructed`），由 `fetch_bibtex.py` 维护，勿手改。`references.bib` 由 `generate_bibtex.py` 从缓存 + frontmatter 组装。
