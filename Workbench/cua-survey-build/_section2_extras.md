## 调研日志

- **迁移来源**：[[Topics/GUIAgent-Survey]] §1 Overview 的 scope 边界段（Deep Research/通用 Agentic RL/通用 VLM/Embodied 排除）与 §2.1 首段 pre-LLM 谱系（Sikuli/RPA/PbD），以及"调研日志"中 2026-07-21/07-22/07-23 三轮检索方法记录；`Topics/CUA-Survey.md` frontmatter 的 keywords/exclude_keywords/exclude_tags/hard_exclude_keywords/exclude_override_tags 字段；`skills/1-literature/survey-refresh/SKILL.md` Step 3 的六字段编码表与 verification_status 定义。
- **vault 新挖**：`Papers/2501-ACUSurvey`（提供 POMDP 形式化与独立制定的 exclusion 边界，对本 section 价值最高）、`Papers/2400-LargeLanguageModelBrained`（补第三篇独立 survey 佐证坐标共识）、`Papers/2605-OpenComputer` 的 GUI vs CLI 直接对照数字（75.2% vs 67.2%，141s vs 288–622s）、`Papers/2508-ComputerRL` 的 GUI vs GUI+API 消融（11.2%→26.2%）、`Papers/2605-EnvTrustBench`（非 GUI-specific 的边界反例）、`Papers/2607-LongHorizonTerminalBench`、`Papers/2604-ClaudeCode`（CLI/coding agent 代表作）、`Papers/2409-WindowsAgentArena`（Desktop/OS Agent 代表 benchmark）。
- **未解决**：programming-by-demonstration 作为独立技术路线（区别于 RPA 规则脚本）在当前 vault 中没有专门 digest 的代表论文，2.1/2.3 中的 PbD 表述仍只依赖 [[Topics/GUIAgent-Survey]] 既有转述，未溯源到 PbD 原始文献；见 gaps。

## Key Evidence Matrix（本 section 新增行）

| Claim | State | Locator | 边界 |
|:--|:--|:--|:--|
| Sikuli 为纯模板匹配、无语义泛化，是 visual macro 而非 agent | source-verified | [[Papers/0910-Sikuli]] | 单一历史工作，非当代基准比较 |
| GPT-4o 框架消融：纯 GUI 11.2% → GUI+API 26.2%（OSWorld，Office 域 6.2%→27.9%） | source-verified | [[Papers/2508-ComputerRL]] §Key Results | 单一 backbone（GPT-4o）+ 单一系统内消融，非跨系统通用结论 |
| 14 应用/343 任务上 GUI 75.2% vs CLI 67.2%，CLI 更快（141s vs 288–622s） | source-verified | [[Papers/2605-OpenComputer]] Ablation: GUI vs. CLI Agents | 单一 benchmark 内对照，未跨其他平台复现 |
| EnvTrustBench 83.3% 聚合 Environmental Misgrounding Rate，跨 14 个 model-scaffold stack | source-verified | [[Papers/2605-EnvTrustBench]] | scope 为通用 CLI/coding agent，非 GUI-specific，仅作邻接证据 |
| LLM-Brained / OS Agents / ACU 三篇独立 survey 收敛于"平台 × 观察-动作原语"坐标 | 跨来源收敛（3 篇独立 survey），非单篇共识声明 | [[Papers/2400-LargeLanguageModelBrained]]、[[Papers/2508-OSAgentsSurvey]]、[[Papers/2501-ACUSurvey]] | 三者对"CLI/API action 是否算一等公民"未统一，见 §2.3 |