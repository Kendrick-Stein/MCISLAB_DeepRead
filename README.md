# ReadPaperMachine

AI-assisted research knowledge management system inspired by [MindFlow](https://github.com/liqing-ustc/mindflow).

## 理念

ReadPaperMachine 是一个基于 Obsidian 的科研知识管理系统。核心理念：

- **Markdown-native**：一切皆文件，一切可读，一切有版本控制
- **AI-driven**：AI Agent 作为 Researcher，阅读技能定义（SKILL.md）后直接读写 Markdown 文件执行工作流
- **Zero backend**：无需 Python 后端、数据库或 API 层。Vault 就是应用状态

## 目录结构

```
ReadPaperMachine/
├── Papers/              # 论文笔记（YYMM-ShortTitle.md）
├── Topics/              # 文献调研与分析报告
├── Ideas/               # 研究 idea
├── DomainMaps/          # 核心认知地图
├── Reports/             # 生成的报告
├── Projects/            # 项目追踪
├── Meetings/            # 会议记录
│
├── Templates/           # 笔记模板
├── skills/              # 科研 Skill 定义（13 个）
├── references/          # 协议文档
│
├── Workbench/           # Researcher 工作状态
│   ├── agenda.md        # 研究议程
│   ├── queue.md         # 待办队列
│   ├── memory/          # 蒸馏记忆
│   ├── logs/            # 每日操作日志
│   └── evolution/       # 演化记录
│
├── docs/SPEC.md         # 系统规范
└── AGENTS.md            # Researcher 身份与指令
```

## Skill 系统

所有科研工作流通过 `skills/` 中的 Markdown Skill 文件定义：

| 类别 | Skills |
|:-----|:-------|
| 1-literature | `paper-digest`, `literature-survey` |
| 2-ideation | `idea-generate`, `idea-evaluate` |
| 3-experiment | `experiment-design`, `experiment-track`, `result-analysis` |
| 4-writing | `draft-section`, `writing-refine` |
| 5-evolution | `memory-distill`, `agenda-evolve`, `memory-retrieve` |
| 6-orchestration | `autoresearch` |

每个 Skill 定义在 `skills/<category>/<name>/SKILL.md`，AI Agent 读取后按 Steps 执行，遵守 Guard 约束，通过 Verify 检查。

## 使用方式

本系统设计为与 Claude Code 或其他 AI Coding Agent 配合使用。Agent 作为 Researcher，按照 `AGENTS.md` 中定义的身份和研究原则自主工作。

**日常使用**：
- 直接让 Agent 执行 `/paper-digest <url>` 消化论文
- 让 Agent 自主推进研究：`autoresearch`

## License

MIT
