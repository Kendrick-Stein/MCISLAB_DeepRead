# ReadPaperMachine Specification

> 本文件是 ReadPaperMachine 的 single source of truth。

**Last updated**: 2026-04-28

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
├── Papers/              # 论文笔记（YYMM-ShortTitle.md）
├── Ideas/               # 研究 idea
├── Projects/            # 项目追踪
├── Topics/              # 文献调研 / 跨论文分析报告
├── Reports/             # 生成的报告
├── Meetings/            # 会议记录
│
├── DomainMaps/          # 核心认知地图
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
│   └── 6-orchestration/ #   编排技能
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
| `2-ideation` | `idea-generate` | 从知识空白生成研究 idea |
| | `idea-evaluate` | 评估 idea 可行性和新颖性 |
| `3-experiment` | `experiment-design` | 设计实验方案 |
| | `experiment-track` | 记录实验进展和结果 |
| | `result-analysis` | 分析实验结果，提取 insight |
| `4-writing` | `draft-section` | 起草论文/报告章节 |
| | `writing-refine` | 打磨已有文稿 |
| `5-evolution` | `memory-distill` | 从日志蒸馏记忆 |
| | `agenda-evolve` | 演化研究议程 |
| | `memory-retrieve` | 从记忆库检索相关经验 |
| `6-orchestration` | `autoresearch` | 核心研究循环 |
