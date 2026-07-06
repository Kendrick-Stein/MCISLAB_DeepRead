# EvoSkills Attribution

本 vault 的部分 skill 移植（vendor）自 [EvoScientist/EvoSkills](https://github.com/EvoScientist/EvoSkills)。

- **Source repo**: https://github.com/EvoScientist/EvoSkills
- **License**: Apache License 2.0（原文见 [EvoSkills-Apache-2.0.txt](EvoSkills-Apache-2.0.txt)）
- **Vendor date**: 2026-07-06

## 已移植的 skill（本批次，5 个）

| Skill | Vault 路径 |
|---|---|
| `paper-planning` | `skills/4-writing/paper-planning/` |
| `paper-review` | `skills/4-writing/paper-review/` |
| `paper-rebuttal` | `skills/4-writing/paper-rebuttal/` |
| `paper-writing` | `skills/4-writing/paper-writing/` |
| `academic-slides` | `skills/7-presentation/academic-slides/` |

## 计划移植（后续批次，2 个）

| Skill | 状态 |
|---|---|
| `paper-figures` | 未移植，后续批次引入 |
| `paper-graph` | 未移植，后续批次引入 |

以上共 7 个 skill 构成本次 EvoSkills vendoring 的完整范围。EvoSkills 仓库中的其余 skill（`evo-memory`、`evomath-tao`、`experiment-craft`、`experiment-iterative-coder`、`experiment-pipeline`、`nano-banana`、`paper-navigator`、`research-ideation`、`research-survey`）未移植，本 vault 使用自有的等价 skill（见下方 adaptation summary）。

## Adaptation Summary

对每个移植的 SKILL.md 做了以下本地化适配，内容方法论保持不变：

1. **`allowed-tools` 重映射**：EvoScientist 工具名（`write_file` `edit_file` `read_file` `think_tool` `execute`）→ Claude Code 工具名（`Read, Write, Edit, Glob, Grep`，`academic-slides` 额外加 `Bash` 用于生成 `.pptx`）。
2. **frontmatter `metadata`**：保留原有 `author`/`version`/`tags`，新增 `source: EvoScientist/EvoSkills` 与 `license: Apache-2.0`。
3. **新增 `## Guard` 与 `## Verify`**：为每个 skill 补充符合 `references/skill-protocol.md` 的行为约束与输出校验清单（原始 EvoSkills 内容中隐含的规则被显式化）。
4. **交叉引用重映射**（指向未移植的 EvoSkills）：
   - `research-ideation` → `idea-generate` / `idea-evaluate`
   - `experiment-pipeline` / `experiment-craft` → `experiment-design` / `experiment-track` / `result-analysis`（产出改为指向 `Experiments/` 记录）
   - `paper-navigator` → `paper-digest` / `literature-survey`
   - `evo-memory` → `Workbench/memory/`
   - `paper-writing` 的 Related Work 小节额外指向本 vault 的 `related-work` skill（确保 `\cite` 可溯源到 `references.bib`），原 `related-work-guide.md` 保留作为写作质量参考
5. **协议整形**：为每个文件补齐 `## Purpose` 与 `## Steps` 两个必需 section（原文多为 `# Title` + `## When to Use` + 主题式小节），内容未改写，仅做标题降级/包裹。
6. **署名头**：每个 SKILL.md 的 frontmatter 之后新增一行 `> Vendored from EvoScientist/EvoSkills ...` 指回本文件与 license 原文。

内容（Steps 的方法论、references/*.md 指南、assets/* 模板）本身未作实质性改写，仅在少数 reference 文件中同样做了交叉引用重映射（例如 `paper-writing/references/writing-practice.md` 中 "research-ideation" → 本 vault 的 `paper-digest`）。
