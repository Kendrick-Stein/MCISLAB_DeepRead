---
title: "Representation-Selection Regret：固定观察表示在 web agent 上留下多少可收回的成功率"
tags: [gui-agent, web-agent, research-idea]
status: raw
linked_project:
date_updated: "2026-07-23"
---
## Hypothesis

web agent 每一步都在某个固定的观察表示下决策（全 a11y tree、全 HTML、或某种固定 reduction）。[[Papers/2604-ReadMoreThinkMore]] 已证明"最优表示取决于 model capability × thinking budget"，但它给的是**每模型一条静态规则**（弱模型→a11y、强模型→HTML）。假设：**最优表示在同一 episode 内随页面变化，固定表示（含 Read-More 的静态每模型规则）因此留下可测量的成功率差距（representation-selection regret）**。

该假设不依赖任何表示分类学。可证伪预测：

- 在每个决策步用可复位环境从**同一状态**分叉、让 frozen policy 在候选表示集 R 下各跑一次到终局，逐步最优选择（oracle over R）与**最强固定表示**、以及与 **Read-More 静态每模型规则**之间的任务成功率差距 ≥5pp（同 backbone、同 step budget、frozen continuation 下测）；
- 一个部署时无需分叉的 selector（cheap page features 起步，分叉数据可训练）能收回该差距的 ≥50%；
- **Kill criterion**：若 Read-More 静态每模型规则在 task-cluster 95% CI 下已捕获 per-step oracle 的 ≥85% 价值，则 per-page 路由不值得做，假设证伪——regret 测量本身作为负结果报告。

候选表示集（有限、预注册，非分类学）：① 全 a11y tree；② 全 HTML（含 CSS layout）；③ a11y + screenshot（hybrid）；④ retrieval-reduced a11y（FocusAgent 式选行）；⑤ diff-based history 表示（Read-More 的 token-efficient 变体）。事后按 outcome vector 聚类页面类型，只把类别当实验输出。

## Motivation

### 问题为什么重要且现在能做

"喂优化版 DOM 而非 raw DOM"这条线已方法饱和（见 [[Topics/GUIAgent-Survey]] §2.1），但一个基本的部署决策仍无证据支撑：**给定一个 agent，运行时到底该用哪种表示？** Read-More 把答案锁在"每模型一条静态规则"上，可它自己的 Table 3 就显示 HTML 的收益**按任务类别分化**（Filter/Sort/Dashboard↑、Form/Knowledge/Catalog↓）——这直接暗示最优表示是 **page-level** 而非 model-level 的属性。若真如此，任何固定表示（包括静态规则）都在系统性丢分，而这个 gap 从未被直接测过。

现在能做的两个条件都已就绪：(1) 可复位的 deterministic web 环境（WorkArena sandbox、[[Papers/2504-REAL]]、WebArena self-hosted）让 same-state fork 可行；(2) [[Papers/2605-MFSCoverage]] 提供了无需 web access/LLM 推理的廉价 value proxy，可把"全 fork 测 SR"的成本压下来做大规模 pilot。

### 机制假设（为什么 per-page 会赢）

表示的价值随页面结构变化：**dense-layout 页面**（表格、多筛选器、dashboard）里 HTML 的 CSS/层级 token 承载 a11y 丢失的空间与遮挡线索，[[Papers/2604-ReadMoreThinkMore]] 的 error analysis 证明强模型正是靠这些 layout 线索降低 intercepted error；而**简单文本/表单页面**里 HTML 的 formatting token 是纯噪声，弱模型在更长输入下 hallucination 上升。同一任务的 episode 会同时穿过这两类页面，所以逐页选择的上限高于任何 per-episode-fixed 选择。这一 page-heterogeneity 是可测的机制，不是"adaptive 总是好"的空泛主张。

### 已知 / 未被证明

- **已知**：Read-More 静态规则有效但粗（per-model、per-category 聚合）；[[Papers/2511-Prune4Web]] 的 0.5B 与 3B grounder 在剪枝后打平（88.28%），暗示"表示质量可替代模型容量"；[[Papers/2410-AgentOccam]] 证明表示重构的杠杆是对齐/降噪而非长度。
- **尚未被证明**：在同一 web 状态分布上，oracle 对候选表示的逐步选择比最强固定表示 / 静态规则高 ≥5pp。这个量必须由 matched-state intervention 测出，不能由 per-category 差异拼接推断。

## Related Work
- [[Papers/2604-ReadMoreThinkMore]] - 最近邻先验：capability × thinking budget 决定表示，但只给**静态每模型规则**，无 per-step oracle、无 selector、无 regret 测量。本工作的 baseline 与被挑战对象。
- [[Papers/2605-MFSCoverage]] - 廉价评测代理（MFS coverage）；可被**复用**为本工作的 value proxy 做低成本 pilot，但它评测的是 element-reduction 的信息保全，不是 representation-choice 的 SR，需先验证 proxy 对本任务成立。
- [[Papers/2410-AgentOccam]]、[[Papers/2511-Prune4Web]]、[[Papers/2510-FocusAgent]] - 三种**固定**表示/reduction 方法，构成候选表示集的来源，不做 per-step 选择。
- [[Papers/2512-WebOperator]] - 按 a11y tree 大小启发式调整观察空间（size-heuristic adaptation），是"启发式自适应"先例，但无 counterfactual 测量、无 regret、无学习 selector。
- [Agent-E](https://arxiv.org/abs/2407.13032) - 提供 text_only/input_fields/all_fields 三种表示并按任务启发式选择 + fallback；证明"per-task 表示选择"已有先例，本工作差异是 **same-state counterfactual matrix + regret vs 静态规则 + fork-free selector**。
- [Causal Agent Replay / CausalFlow](https://arxiv.org/abs/2606.08275) - per-step counterfactual **归因**（哪一步导致失败），与本工作的 per-step **选择**不同；但其"run-forward resampling 会让无关早步显效"的警告是本工作必须处理的方法学 confound。
- [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] - 共享"same-checkpoint counterfactual matrix + fork-free selector"的测量模板；本 idea 把该模板从 recovery-action 选择迁到 observation-representation 选择（不同问题、不同机制假设，非同一工作）。

**Novelty**: 3/5 — closest works: [[Papers/2604-ReadMoreThinkMore]]、[Agent-E](https://arxiv.org/abs/2407.13032)、[[Papers/2512-WebOperator]]。广义的"自适应表示选择"已被 Agent-E / WebOperator / Read-More 占据；可守的新颖性是三者组合：**web 同状态全表示 counterfactual value matrix + per-step oracle vs 最强固定/静态规则的 regret 直接测量 + outcome-value selector 的 fork-free 部署**。

更安全的 claim：

> 据我们所知，现有 web-agent 工作尚未在同一决策状态上，对一组预定义、可执行的观察表示做可复位分叉、以 terminal outcome 估计完整 counterfactual value vector，并据此直接量化 per-step oracle 与最优固定表示（含 capability-aware 静态规则）之间的 representation-selection regret。

不再声称：representation selection 本身无人研究；所有方法都用固定表示；capability-aware 选择是新概念。

## Approach sketch

沿用 [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] 的"先测 headroom 再谈 selector"两层协议。

**Phase 0（proxy + fork fidelity）**：先用 [[Papers/2605-MFSCoverage]] 的 coverage 作廉价 proxy，在大样本上标出"表示分歧最大"的页面（不同表示保留的 MFS 差异大处），锁定值得全 fork 的子集；同时在 deterministic web mirror（REAL / WorkArena sandbox）上验证 same-state restore 等价（screenshot / DOM / back stack / backend state diff），报告 restore divergence rate。禁用 live 站点作主实验（backend 不可复位）。

**Phase 1（per-step state bank）**：至少一强（如 claude-sonnet 级）一弱（如 gpt-oss-20b 级）两个 frozen policy 各跑 WorkArena L1（复用 Read-More 的 exact setting 以直接对照其静态规则）+ WebArena。每个决策步记录状态与部署可用特征。first-decision-per-page 为主反事实单位，避免长 episode 贡献大量相关点。

**Phase 2（matched-state representation matrix）**：对每个采样步，从同一 checkpoint 分叉，用**完全相同的 frozen continuation policy** 在每种候选表示下续跑到终局或统一 step cap。为隔离"当前这一步的表示选择"，续跑段固定使用同一预注册表示（frozen continuation），并用独立 replicates / cross-fitting 估值——直接回应 run-forward resampling 的 confound。估计 Q_page(r) = P(task success ∧ ¬harmful side effect | do(use r at this step), frozen continuation)。

**Phase 3（regret / kill，零训练）**：比较 {每个固定表示、validation-selected 最强固定、Read-More 静态每模型规则、Agent-E 式 size-heuristic、per-page oracle}。主表报 conditional SR、H_fork（oracle − best fixed）、oracle − 静态规则、feasible coverage、成本、task-cluster 95% CI。按预注册 decision rule 判 Go / Kill / Inconclusive。

**Phase 4（fork-free selector）**：从廉价 page features（a11y token 数、DOM 深度、interactive 元素密度、是否含 table/filter、model-capability proxy 如 long-context retrieval 得分）预测每种表示的 Q̂ 与 cost，argmax 选择。三档：rule/threshold router（回答"是否规则就够"）、prompted selector、learned selector（直接最小化 counterfactual regret，非 hard-class）。

**Phase 5（端到端部署）**：从任务起点闭环比较 {固定表示、静态规则、rule router、prompted/learned selector}，报 SR、Δ best-fixed、token/latency 成本、side effects；paired hierarchical bootstrap（task→seed），不把 step 当 iid。

## Expected outcome

若假设成立：

- WorkArena L1 上 per-page oracle over R 比最强固定表示 **且** 比 Read-More 静态规则高 ≥5pp（task-cluster CI 下界 >3pp）；
- regret 集中在少数页面类型（dense filter/table/dashboard ↔ HTML；simple form/text ↔ a11y），事后聚类可解释；
- 一个只看廉价 page features 的 learned selector 收回 ≥50% headroom，且 fork-free 部署时端到端 SR 显著超最强固定表示与静态规则；
- 弱模型的 regret 主要来自"该用 a11y 时误用 HTML 导致 hallucination"，强模型的 regret 主要来自"该用 HTML 时误用 a11y 丢 layout"——与机制假设方向一致。

成功标准：两个 base agent、两个 benchmark 上 H_fork 与 CI 同时成立，且 selector 端到端增益可复现。**Kill 也是有价值产出**：给出"per-page 路由不值得、静态规则已足够"的可信负结论（含 detector-free 的干净测量）。

## Risk

- **Novelty 有强邻居**：Agent-E / WebOperator 已做启发式表示选择，Read-More 已给静态规则。论文必须以 same-state regret measurement 为第一贡献、selector 为第二，绝不声称"自适应选择是新的"。若测得 regret < 静态规则的 15%，idea 降为负结果论文。
- **静态规则可能已足够（主 kill 风险）**：Read-More 的 per-model 规则若已捕获绝大部分 headroom，则 per-page 无价值——这正是 kill criterion 要直接裁决的。
- **Fork fidelity（web 尤重）**：backend state、session、network、支付/提交等 non-idempotent 转移可能不在快照内。fork fidelity 是前置 gate，只用 deterministic mirror，不用 live。
- **run-forward resampling confound**：per-step counterfactual 下早步会因 re-roll 下游 pivotal step 而显效（CausalFlow 已警告）。用 frozen continuation + 独立 selection/evaluation replicates 隔离当前表示选择。
- **MFS proxy 可能不迁移**：coverage 面向 element-reduction，未必预测 representation-choice 的 SR。Phase 0 必须用一小批全 fork 校验 proxy 相关性，不成立则 proxy 只用于 pilot 采样、不进主结论。
- **成本**：steps × |R| × suffix × replicates 很大；用 MFS proxy 预筛 + first-decision-per-page + adaptive replication 控制，先做 30–50 页 pilot 再定规模。

## Evaluation — 2026-07-23（首轮，novelty-verified）

| Dimension | Score | Notes |
|:--|:--:|:--|
| Novelty | 3/5 | 自适应表示选择被 Agent-E/WebOperator/Read-More 占据；same-state representation regret + fork-free selector 可守，但需以测量为第一贡献 |
| Feasibility | 4/5 | 可复用 WorkArena L1 exact setting + MFS proxy + frozen policies，核心测量零训练；web fork fidelity 与规模需先 pilot |
| Impact | 4/5 | 直接裁决"运行时该用哪种表示"这一未答的部署问题；positive / well-powered negative 都有价值 |
| Risk | 3/5 | 主 kill 风险=静态规则已足够；fork fidelity、proxy 迁移、resampling confound 均可能改结论，但分阶段 gate 可控沉没成本 |
| Evidence | 4/5 | Read-More per-category 分化 + AgentOccam 对齐悖论 + Prune4Web 0.5B=3B 共同支持 page/representation heterogeneity；无论文测过 per-step regret |
| **Total** | **18/25** | 值得做，但价值取决于 Phase 0–3 能否同时证明 fork fidelity、统计功效与 H_fork |

**Reasoning**：这是把 [[Ideas/MismatchTriage-LongHorizonRecovery-GUI]] 已验证的测量模板迁到一个真正未被测量的量（web 观察表示的 same-state selection regret）。最强贡献是"证明 per-page 表示选择相对静态规则有 / 无可收回 headroom"，selector 只有在 headroom 成立后才值得训练。

**Suggested next action**：先做 30–50 个决策步的 no-training pilot，只回答四问——web mirror 的 fork 是否等价、MFS proxy 是否预测 representation-choice SR、Read-More 静态规则离 per-page oracle 差多少、需要多少 task/seed 把 3pp 与 5pp 区分开。任一答案不理想即在训练 selector 前 pivot。

## Novelty search log — 2026-07-23

- `adaptive observation representation selection web agent learned router HTML accessibility tree per-step` → 命中 Read-More、Agent-E（per-task 启发式选择）、WebOperator（size-heuristic）、cotomi Act（adaptive observation scaffold）；搜索明确"未找到 trained/learned per-step router，属 open direction"。
- `dynamic input representation switching LLM agent capability-aware DOM vs a11y tree` → capability-aware 概念被 Read-More 支撑；自适应观察空间由 WebOperator 等启发式实现；无 counterfactual regret 测量。
- `counterfactual measurement observation representation choice web agent oracle regret fixed vs per-step success rate` → 无直接对照"fixed vs per-step 表示 SR"的论文；最近的 CausalFlow / Causal Agent Replay 是 per-step **归因**（非选择），并给出 run-forward resampling confound 警告。
- 结论：per-step representation-selection **regret 测量** + fork-free selector 未被占据；"自适应表示选择"本身已拥挤，故 claim 收窄到测量。
