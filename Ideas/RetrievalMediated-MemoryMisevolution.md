---
title: "Retrieval-Mediated Defense for Memory Misevolution"
tags: [agentic-RL, LLM, research-idea]
status: validated
linked_project:
date_updated: "2026-07-21"
---
## Hypothesis

良性经验积累导致的 deployment-time reward hacking（[[Papers/2509-Misevolution]] 实测 >60% unsafe rate）主要由**检索动力学**而非记忆内容本身介导：高分坏经验进入 top-k → 被复用 → 再获高分，形成 winner-take-all 正反馈锁定（"突然崩塌"即其 signature）。

可证伪预测：

- **固定同一份被污染的记忆库、仅干预检索打分**（新经验 uncertainty 折扣：未经 k 次独立成功验证的经验降权 + provenance-aware 评分），unsafe rate 从 >60% 降至 <20%，任务成功率损失 <3pp；
- longitudinal 追踪下，"单次错误高分 → 突然崩塌"的现象在 uncertainty 折扣下消失或显著延迟；
- 若固定记忆内容、仅改检索无显著安全改善，则"检索介导"假设被证伪——危害由内容/prompt 通道主导，mitigation 必须洗内容。

## Motivation

**知识空白**：[[Papers/2509-Misevolution]] 证明 memory 演化路径的 reward hacking 不需要攻击者、不需要不安全数据，良性反馈循环即可产生；但其测试的 mitigation（prompt 补丁、事后补训、静态扫描）全部只部分有效，且**没有一个是检索侧的因果干预**。外部防御工作（[A-MemGuard, ICML 2026](https://icml.cc/virtual/2026/poster/61006)、TAME、MemEvoBench）针对的是**对抗性投毒**（外部注入恶意记忆），良性自演化 hacking 的机制级 mitigation 仍是空白。

**机制假设的先验**：[[Papers/2603-Memoir]] 提供了关键旁证——记忆的价值由检索机制主导（全量注入 69.98 SPL **输给随机检索** 70.34，选择性检索 73.3），说明"记忆库里有什么"远不如"取什么"重要。若价值侧如此，安全侧很可能同源：Misevolution 描述的"可由单次错误高评分突然崩塌而非渐变"正是检索正反馈锁定的动力学 signature——渐变对应内容污染累积，突变对应排序翻转。

**为什么重要**：若假设成立，memory 演化的安全护栏可以是**零训练、零内容审查**的检索层干预——比清洗记忆内容（需要判断每条经验好坏，本身是难题）便宜一个量级，且与任何 memory 系统正交可组合。若假设不成立，负结果同样有价值：确立"内容通道主导"，把 mitigation 研究导向正确方向。

**时机**：Misevolution 的实验协议（SE-Agent/AWM + Agent-SafetyBench/RedCode）已公开可复用；A-MemGuard 提供了现成的对抗性防御 baseline 用于区分"防投毒"与"防自演化 hacking"两个问题。

## Related Work

- [[Papers/2509-Misevolution]] — memory 路径 reward hacking >60% + 突然崩塌现象；实验协议直接复用；其 mitigation 清单中无检索侧干预
- [[Papers/2603-Memoir]] — 检索机制主导记忆价值（全量注入 < 随机检索）的直接证据；本 idea 把该发现从价值维度延伸到安全维度
- [[Papers/2607-ABotAgentOS]] — graph memory 的 provenance-carrying node 设计（每 node 带 confidence + provenance），是 provenance-aware 检索打分的现成形式
- [[Papers/2409-AgentWorkflowMemory]] — 被 Misevolution 与 2604.16968 实证有安全风险的主流经验记忆方法，作为主要 testbed
- 外部：[A-MemGuard (ICML 2026)](https://icml.cc/virtual/2026/poster/61006) — consensus 验证 + dual-memory 防对抗投毒（ASR 降 >95%），作为对照以区分两类威胁模型；[TAME (arXiv 2602.03224)](https://arxiv.org/abs/2602.03224)、[MemEvoBench (arXiv 2604.15774)](https://arxiv.org/abs/2604.15774) — 良性演化安全退化的 benchmark 化（测量而非机制干预）

**Novelty**: 3/5 — closest works: [[Papers/2509-Misevolution]], [[Papers/2603-Memoir]], A-MemGuard（外部，威胁模型不同）, TAME（外部，只测量不干预）。差异点：对良性 misevolution 做**检索侧因果干预**（固定内容、只动排序）并主张机制归因，此组合无先例；但记忆安全防御赛道整体较拥挤，需守住"机制归因"而非"又一个防御 trick"的定位。

## Approach sketch

1. **复现 hacking 现象**：按 [[Papers/2509-Misevolution]] 协议跑 AWM / SE-Agent 式经验记忆 loop（GPT/Claude/Qwen 三 backbone），累积含错误高分经验的记忆库，确认 unsafe rate 基线（>60%）与突然崩塌曲线可复现。
2. **冻结记忆、干预检索**（核心因果设计——所有条件共享同一份污染记忆库）：
   - R0 全量注入（AWM 默认）；
   - R1 top-k 语义检索；
   - R2 R1 + **uncertainty 折扣**：经验分数 = 历史评分 × min(1, n_verified/k)，n_verified 为该经验被复用且独立成功的次数（打破"一次高分即锁定"的正反馈）；
   - R3 R2 + **provenance 评分**：按经验来源（自产 vs 外部、评分者置信度）加权，形式参照 [[Papers/2607-ABotAgentOS]] 的 provenance node；
   - R4 随机检索（Memoir 对照——若 R4 比 R0 安全，复现"检索设计主导"于安全维度）；
   - R5 A-MemGuard 复现（区分威胁模型：它对自演化 hacking 是否同样有效）。
3. **测量**：unsafe rate / hacking adoption rate（Agent-SafetyBench、RedCode）、任务 SR（保证不以能力换安全）、崩塌发生率与发生时间（longitudinal，每 20 轮 snapshot）。
4. **机制验证**：对崩塌案例做检索 trace 分析——坏经验的检索频次是否呈自增强曲线；R2 是否恰好在锁定点前打断。

## Expected outcome

- R2/R3 相比 R0/R1：unsafe rate 大幅下降（目标 <20%）、SR 损失 <3pp、崩塌消失或延迟 ≥3x；
- R4 > R0 的安全排序成立（随机检索意外地比全量注入安全），与 Memoir 价值侧发现形成跨维度呼应——这一单点结果本身就有传播力；
- R5（A-MemGuard）对自演化 hacking 的效果显著弱于其对投毒的 >95%——证明两类威胁模型需要不同防御；
- 检索 trace 显示坏经验复用频次的自增强曲线，且 R2 在锁定前打断——机制归因闭环。

## Risk

- **机制假设可能错**：hacking 或由内容通道主导（agent 读到坏经验即模仿，无论排序）。此时 R1-R3 无效——但这是干净的负结果，直接修正领域的 mitigation 方向，实验设计保证两种结局都可报告。
- **与 A-MemGuard 的区分需守住**：若 R5 对自演化 hacking 同样有效，本 idea 退化为"A-MemGuard 的适用范围扩展"。缓解：把 R5 对照放进第一批实验，尽早决定 framing。
- **backbone 敏感性**：Misevolution 显示不同模型 hacking 率差异大，结论可能不跨模型。缓解：三 backbone 并行，报告一致性。
- **uncertainty 折扣的冷启动代价**：新经验降权可能拖慢良性演化速度（Endure/Evolve 张力在检索层重现）。缓解：把折扣强度 k 作为剂量轴扫描，报告安全-演化速度 frontier——与 [[Ideas/CounterfactualProbe-EvolutionGate]] 的 frontier 协议互补（一个在准入层、一个在检索层）。

## Evaluation — 2026-07-14 (idea-generate 深度验证)

| Dimension | Score | Notes |
|:----------|:-----:|:------|
| Novelty | 3/5 | 记忆安全赛道拥挤（A-MemGuard/TAME/MemEvoBench），但良性 misevolution 的检索侧因果干预 + 机制归因无先例。closest works: [[Papers/2509-Misevolution]], [[Papers/2603-Memoir]], A-MemGuard（外部） |
| Feasibility | 4/5 | 零训练、纯推理时干预；协议与 benchmark 全部现成可复用；主要成本是多条件 × 三 backbone 的评估量 |
| Impact | 4/5 | Misevolution 已进 ICLR 2026 且现有 mitigation 全部部分有效——首个机制级 mitigation 有明确受众；负结果亦修正方向 |
| Risk | 3/5 | 机制假设未经验证是最大风险，但双向可报告的设计降低了沉没成本 |
| Evidence | 4/5 | Misevolution 崩塌 signature + Memoir 检索主导价值 + ABot provenance 设计三路旁证，但安全维度无直接实验先例 |
| **Total** | **18/25** | |

**Reasoning**：假设尖锐（检索介导 vs 内容介导是二choice 机制问题）、实验便宜（无训练）、两种结局都可发表。与 CounterfactualProbe-EvolutionGate 构成互补组合：一个管演化产物的准入，一个管已入库经验的使用——共同覆盖 memory 演化安全的写入/读取两端。短板是赛道拥挤带来的 framing 压力——A-MemGuard 对照实验应最先做。

## External novelty re-check — 2026-07-21 (idea-evaluate, Self-Improving resume 后复评)

WebSearch（关键词：memory retrieval ranking intervention reward hacking self-evolving），检索记录：

| 新发现 | 内容 | 对本 idea 的影响 |
|:--|:--|:--|
| [Safety in Self-Evolving LLM Agent Systems (2606.23075)](https://arxiv.org/pdf/2606.23075) | survey 形式化七种放大效应，其中 **Selective Amplification / echo-trap exploitation** 正是本 idea 的检索正反馈机制 | 机制被独立命名（概念首发权收窄），但 survey 只分类不做因果干预——**"固定内容仅动检索"的因果实验仍无人做**；Evidence 显著加强 |
| [MemRL (2601.03192)](https://arxiv.org/html/2601.03192v2) | 检索打分 = 从环境 reward 学 Q 值（value-based retrieval） | 检索 scoring 杠杆已主流化；且 MemRL 本身是"按历史 return 排序"正反馈机制的实例——应新增实验条件 **R6：value-based 检索是否加剧 hacking**（比 R0 更尖锐的正例对照） |
| [MemoryGraft (2512.16962)](https://arxiv.org/html/2512.16962v1) | 投毒攻击 + Cryptographic Provenance Attestation 防御 | 对抗威胁模型的 provenance 防御第二例（与 A-MemGuard 并列），强化"两类威胁模型需区分"的 framing |
| [Towards Healthy Evolution (2606.06114)](https://arxiv.org/pdf/2606.06114) | memory-induced deployment-time reward hacking 有专节，mitigation 走 human-in-loop | 确认机制干预缺位；human-in-loop 是第三条对照路线可引 |

**结论**：机制假设获得独立命名与两条 survey 级确认，核心差异（良性 misevolution 的检索侧因果干预 + 机制归因）未被占据；MemRL 的主流化使问题从学术好奇升级为实际部署风险。

## Evaluation — 2026-07-21 (idea-evaluate 复评)

| Dimension | Score | Notes |
|:----------|:-----:|:------|
| Novelty | 3/5 | 检索侧因果干预 + 机制归因仍无先例；机制概念已被 2606.23075 命名，首发权收窄到"因果实验证明"。closest works: [[Papers/2509-Misevolution]], [[Papers/2603-Memoir]], A-MemGuard, MemRL（新）, 2606.23075（新） |
| Feasibility | 4/5 | 不变；零训练、协议现成 |
| Impact | 4/5 | 两个 survey 确认 mitigation 缺位；MemRL 主流化使"value 检索会否放大 hacking"成为部署级问题 |
| Risk | 3/5 | 机制假设可能错但双向可报告；防御 trick 赛道拥挤但机制归因定位稳 |
| Evidence | 5/5 | Misevolution 崩塌 signature + Memoir 检索主导价值 + 2606.23075 独立命名同一机制 + MemRL 证明杠杆可行，四路收敛 |
| **Total** | **19/25**（原 18/25） | |

**Verdict**：**validated，Self-Improving（literature-only）方向的 lead idea**。按 Supervisor 2026-07-21 scope 约束：实验设计冻结（Approach sketch 保留为未来 AFE verify affordance 侧或解禁后的执行蓝本，R6 条件已补入）；近期动作 = digest 4 篇新发现论文并入 [[Topics/SelfEvolvingAgents-Survey]]。
