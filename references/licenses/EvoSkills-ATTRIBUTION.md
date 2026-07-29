# EvoSkills Attribution

本 vault 的部分 skill 移植（vendor）自 [EvoScientist/EvoSkills](https://github.com/EvoScientist/EvoSkills)。

- **Source repo**: https://github.com/EvoScientist/EvoSkills
- **License**: Apache License 2.0（原文见 [EvoSkills-Apache-2.0.txt](EvoSkills-Apache-2.0.txt)）
- **Vendor date**: 2026-07-06（首批 5 个）/ 2026-07-06（第二批 2 个，`paper-figures` / `paper-graph`）

## 已移植的 skill（共 7 个）

| Skill | Vault 路径 | 批次 |
|---|---|---|
| `paper-planning` | `skills/4-writing/paper-planning/` | 第一批 |
| `paper-review` | `skills/4-writing/paper-review/` | 第一批 |
| `paper-rebuttal` | `skills/4-writing/paper-rebuttal/` | 第一批 |
| `paper-writing` | `skills/4-writing/paper-writing/` | 第一批 |
| `academic-slides` | `skills/7-presentation/academic-slides/` | 第一批 |
| `paper-figures` | `skills/4-writing/paper-figures/` | 第二批 |
| `paper-graph` | `skills/7-presentation/paper-graph/` | 第二批 |

以上共 7 个 skill 构成本次 EvoSkills vendoring 的完整范围（无更多后续批次）。EvoSkills 仓库中的其余 skill（`evo-memory`、`evomath-tao`、`experiment-craft`、`experiment-iterative-coder`、`experiment-pipeline`、`nano-banana`、`paper-navigator`、`research-ideation`、`research-survey`）未移植，本 vault 使用自有的等价 skill（见下方 adaptation summary）。

## 第二批（`paper-figures` / `paper-graph`）的额外说明

- **`paper-figures`**：`scripts/validate_figure.py` 本身只用标准库（`argparse`/`re`/`struct`/`sys`/`pathlib`），但 skill 产出的 `plot.py` 依赖 `matplotlib` 渲染图表。已在 `pyproject.toml` 新增 `[project.optional-dependencies].figures = ["matplotlib>=3.8"]`（可选依赖组，不进入运行时依赖）。原文 "this project uses a uv-managed venv" 的说法不适用于本 vault（本 vault 不用 uv），已改写为 `python3` 优先、`uv` 仅作为用户自备的可选替代。
- **`paper-graph`**：`scripts/` 下是一套完整的 CLI + 数据抓取管线（`cli.py`/`pipeline.py`/`web_api.py`/`deepxiv_client.py`/`config.py`/`mermaid.py` 等），依赖 `httpx`、`python-dotenv`（均非标准库），并要求配置 `S2_API_KEY`（Semantic Scholar API key，必需）与可选的 `DEEPXIV_API_TOKEN`，运行时会直接联网调用外部 API。**这些依赖未加入 `pyproject.toml`**——它们不是简单的绘图/解析库，而是需要用户自行申请 API key、可能受限于沙箱网络策略的外部服务集成，性质与 `matplotlib` 不同，故未比照 `paper-figures` 自动加入可选依赖组。已在 `SKILL.md` 的 Purpose/Setup/Guard 中显式标注：vault 内默认优先用 `Papers/` 已读论文构图，只有用户自行安装好 `httpx`/`python-dotenv`（/`deepxiv-sdk`）并配置好 API key 时，才走完整的自动检索 CLI runbook。路径引用也从上游的 `EvoScientist/skills/paper-graph/...` 全量重映射为本 vault 的 `skills/7-presentation/paper-graph/...`（17 处），并将 `uv run python` 统一改为 `python3`（本 vault 无 uv-managed venv）。

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
   - `paper-writing` 的 Related Work 小节额外指向本 vault 的 Related Work 溯源流程（原独立 `related-work` skill，2026-07-28 并入为 `paper-writing/references/related-work-vault.md`；确保 `\cite` 可溯源到 `references.bib`），原 `related-work-guide.md` 保留作为写作质量参考
5. **协议整形**：为每个文件补齐 `## Purpose` 与 `## Steps` 两个必需 section（原文多为 `# Title` + `## When to Use` + 主题式小节），内容未改写，仅做标题降级/包裹。
6. **署名头**：每个 SKILL.md 的 frontmatter 之后新增一行 `> Vendored from EvoScientist/EvoSkills ...` 指回本文件与 license 原文。

内容（Steps 的方法论、references/*.md 指南、assets/* 模板）本身未作实质性改写，仅在少数 reference 文件中同样做了交叉引用重映射（例如 `paper-writing/references/writing-practice.md` 中 "research-ideation" → 本 vault 的 `paper-digest`）。
