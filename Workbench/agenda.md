---
last_updated: "2026-07-03"
updated_by: agenda-evolve
active_topic: GUI Agent
---

## Mission

构建能够可靠理解、定位和操作图形用户界面的视觉 Agent 系统，重点关注 grounding robustness、高效训练范式（RL vs SFT）、以及 self-improving 系统的可靠性保障。长期目标是让 GUI Agent 在跨平台、跨分辨率、动态变化的真实界面中稳定执行长程任务。

---

## Active Directions

### GUI Grounding Robustness

- **priority**: high (secondary — 2026-06-26 起 primary 为 Agent-Facing Environment Runtime；本方向的 grounding 可观测/evidence-dependence 角度可并入 AFE 的 observe/verify affordance)
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: 架构级 multi-scale 设计（FPN + multi-resolution training + consistency loss）可以在不增加推理开销的前提下，显著提升 GUI grounding 在跨分辨率/跨设备场景下的鲁棒性
- **evidence**: [[Topics/GUIAgent-Survey]], [[Papers/2604-GoClick]], [[Ideas/ScaleInvariant-Grounding-GUI]], [[2500-GuiActorCoordinateFree]], [[Papers/2604-AutoGUIv2]] (dichotomy: fine-tuned grounding 强于通用 VLM), [[Papers/2604-WindowsWorld]] (跨应用是独立瓶颈 L1 46% vs L2 14%，grounding 能力比 reasoning 更关键), [[Papers/2605-WorkspaceBench]] (Heterogeneous File Understanding 和 Lineage Tracing 是 workspace agent 瓶颈，最佳 agent 68.7% vs 人类 80.7%，说明 grounding 在复杂环境中仍有显著提升空间), [[Ideas/EvidenceDependence-GUIGrounding]] (18/25, Action Collapse Rate 量化 grounding 是否真正依赖视觉证据), [[Papers/2606-VisualFLIP]] (VLM grounding 评估从单点 accuracy 转向 counterfactual evidence dependence), [[Papers/2606-DecodableNotGrounded]] (灰图 vision-ablation arbiter 推翻 probe+steering 验证的 latent-knowledge 结论，grounded/prior/inverted 三 regime——counterfactual 诊断 pattern 第 3 独立数据点，7/3 已升 provisional insight)
- **next_action**: 实验已重设计为 GUI-Actor baseline（Experiments/2026-04-29-ScaleInvariantGroundingGUI 已更新），下一步：原型验证 FPN + multi-resolution training 在 ScreenSpot-Pro 上的效果（备选低成本切入：用 EvidenceDependence-GUIGrounding 的 Action Collapse Rate 做无训练 grounding evidence-dependence 诊断——可借 DecodableNotGrounded 的三 regime 分类 + 五 ablation protocol 升级设计，且跨分辨率评估可用 arbiter 对照把失败分解为 evidence loss vs prior reliance）
- **confidence**: 0.5 (↑ from 0.45，DecodableNotGrounded 为 evidence-dependence 诊断角度提供独立方法论支撑，counterfactual 诊断 pattern 达 3 数据点升 insight)

### RL-based GUI Agent Training

- **priority**: medium
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: Rule-based RL（GRPO 风格）配合结构化 action reward，可以以 10x 更少的训练数据达到或超越 SFT 的 GUI action prediction 性能，且 OOD 泛化更强
- **evidence**: [[Topics/GUIAgent-Survey]], [[2500-UiR1EnhancingEfficient]], [[Papers/2604-ClawGUI]], [[2500-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]], [[Ideas/ForkPoint-CreditAssignment-GUI]], [[Papers/2604-AutoGUIv2]] (fine-tuning on agent data 对 grounding 有显著增益), [[Papers/2604-SOLAR-RL]] (first failure point detection, 3-stage reward shaping), [[Papers/2602-ProxMO]] (PSC+PSA, 90.6% ALFWorld, state similarity credit assignment), [[Papers/2605-DUDE]] (asymmetric reward ω=10 for deception, hybrid-reward learning 减少 53.8% 欺骗易感性), [[Papers/2605-Skill1]] (unified skill selection/utilization/distillation via single policy, reward signal frequency decomposition for credit assignment), [[Papers/2601-WebGym]] + [[Papers/2606-AsyncWebRL]] (大规模 visual web agent RL：rubric evaluator + async rollout，OOD 泛化来自任务分布 scaling 而非新算法), [[Papers/2606-CUAGym]] (task/state/reward.py 共生成 32K+ verified RLVR tuples，环境侧合成 RL 监督), [[Papers/2606-MobileForge]] (hint-contextualized GRPO：corrective hint 作为 state 条件而非 reward 项，免标注 mobile 自适应，ForgeOwl-8B AndroidWorld 77.6% Pass@3——是 rule/feedback-based reward design 的具体实例), [[Papers/2606-GUIAgentExploration]] (HER 式 hindsight relabeling + TDHAF：low-level 训练无法向上泛化 80.5%→9.1%，组合泛化层级敏感)
- **next_action**: ForkPoint 方向已评估 10/25（ProxMO PSA 概念重叠），建议暂停 credit assignment 子方向，转向 rule-based reward design（更底层、更少竞争）；DUDE 的 asymmetric penalty 和 Skill1 的 frequency-based credit assignment 提供了 reward design 的新视角；需要 Supervisor 决策是否完全放弃 credit assignment
- **confidence**: 0.35 (↑ from 0.3，DUDE asymmetric reward + Skill1 frequency decomposition 为 reward design 提供新思路)

### Agent-Facing Environment Runtime

- **priority**: high (**primary** — Supervisor 2026-06-26 确认为 primary direction，GUI Grounding Robustness 降为 secondary high)
- **status**: exploring
- **origin**: researcher-discovered
- **hypothesis**: 把环境后台已有的 state / reset / verifier / fork 能力以 task-agnostic、non-oracle 的 agent-facing affordance 暴露给 GUI/web/CUA agent，可在 zero/low-training 条件下显著提升 long-horizon task success、wrong-turn recovery，并降低 reward hacking 与 false completion——且该收益不能被 prompt-only baseline 复现
- **evidence**: [[Topics/AgentFriendlyEnvironment-Survey]], [[Topics/ComputerUseAgents-Survey]], [[Topics/GUI-Environment-Survey]], [[Reports/2026-06-23-AgentFriendlyEnvironment-Proposal]], [[Reports/2026-06-24-GUIEnvironment-RecentWorks]], [[Ideas/AgentFacing-WebRuntime]] (18/25), [[Ideas/HybridVerifier-GUIRuntime]] (18/25), [[Papers/2600-WebHarbor]] (真实网站 Docker mirror + 快速 reset), [[Papers/2606-CUAGym]] (32K+ verified RLVR tuples), [[Papers/2605-SaaSBench]] (resolved 3.8%，长程组合可靠性极低), [[Papers/2606-WeaveBench]] (hybrid GUI+CLI+Code，35.2% failure 来自 reward hacking), [[Papers/2605-OpenComputer]] (programmatic verifier 94.1% human alignment > LLM judge), [[Papers/2606-ENVS]] (环境 oracle 可作为 SFT 监督来源), [[Papers/2606-OpenRath]] (Session-as-first-class-value：把碎片化 runtime state 统一为可随程序值流动的 observable state——正是 agent-facing observable affordance 的一种工程实现，但仅 technical report 无 benchmark), [[Papers/2606-AgentMemorySystem]] (12 个 agent memory 系统系统评测；但 workload 全是文本/DB，**完全无 GUI/CUA visual memory 场景**——反向印证 agent-facing memory 在 computer-use 场景仍是空白), [[Papers/2606-PolicyGuard]] (pre-execution sub-agent verifier + 定向 remediation 在 dialogue/tool-call 域实证 runtime verifier affordance：τ²-bench airline Pass⁴ +6~12pp、block rate 减半), [[Papers/2606-Dockerless]] (evidence-grounded verifier 作为 SFT filter + RL reward，接近 test-execution RL), 2 条 7/3 memory insight（"Verifier 角色迁移" 升 **validated**；"runtime state 一等对象化" provisional：OpenRath/MemGUI/ArborHTR/LUMOS/AgenticSTS 五论文收敛——observe affordance 的接口形式有工程收敛证据）
- **next_action**: 在 WebHarbor mirror 或 CUA-Gym-Hub mock apps 上原型化 AFE-MiniSuite（observe/map/rollback/verify affordance + C0–C7 因果对照），先验证 Web-only causal mechanism；prompt-only baseline 必须把 affordance 文本原样塞进 prompt 作为强对照，以排除"收益仅来自信息展示"
- **confidence**: 0.45 (↑ from 0.4，"Verifier 角色迁移" insight 经 Dockerless[SWE]/PolicyGuard[dialogue] 两个新域复现升 validated，verifier affordance 组件的跨域可行性已确立；agent-facing 暴露的因果收益仍无自有实验验证)

---

## Paused Directions

### Self-Improving Agent Reliability

- **priority**: low
- **status**: paused
- **origin**: researcher-discovered
- **hypothesis**: Self-improving GUI Agent 的自增强循环中存在系统性验证偏差，需要外部纠错机制（adversarial verifier 或 self-grounded verification）防止偏差放大
- **evidence**: [[Topics/GUIAgent-Survey]], [[2500-UiGenieSelfImproving]], [[Ideas/AdversarialVerification-SelfImproving-GUI]]
- **pause_reason**: next_action（阅读 SGV / Self-Grounded Verification 论文）自 2026-05-07 起连续无法推进——vault 与 web search 均未找到该论文来源（见 Discussion Topics "SGV 论文来源 — 2026-05-07"）；其 verification debiasing 主题已被新方向 Agent-Facing Environment Runtime 的 [[Ideas/HybridVerifier-GUIRuntime]]（agent-facing cross-channel verifier 降低 reward hacking）更具体地承接
- **resume_condition**: Supervisor 提供 SGV 论文 URL/标题，或出现新的 self-improving verification 论文，或 Agent-Facing Environment Runtime 实验显示需要独立的 self-improving 偏差研究
- **confidence**: 0.15
- **supervisor_note**: 2026-06-26 Supervisor 确认继续暂停

### Personal CUA Safety & Contextual Integrity

- **priority**: low
- **status**: paused
- **origin**: researcher-discovered
- **hypothesis**: personal computer-use agent 的隐私泄露主要来自 normal-use 的 contextual disclosure 而非 adversarial attack；以 task-scoped permission + trajectory-level privacy guard 作为 runtime intervention，可显著降低 inappropriate disclosure，且优于 prompt-level instruction
- **evidence**: [[Ideas/PersonalizedSafety-CUA]] (20/25), [[Papers/2606-AgentCIBench]] (leakage 67.9%), [[Papers/2606-MyPCBench]], [[Papers/2606-BraveGuard]], [[Papers/2606-PrivacyAlign]], [[Papers/2606-OverPrivilegedTools]] (safety-alignment 不迁移到 least-privilege 的 negative result)
- **pause_reason**: Supervisor 2026-06-26 决定 Personal CUA Safety 不在当前 Mission scope 内（Mission 聚焦 grounding/operating GUI 可靠性 + Agent-Facing Environment Runtime）。已积累的证据（AgentCIBench 67.9% leakage、OverPrivilegedTools alignment-不迁移、PrivacyAlign 训练侧对齐）保留备查，不再主动推进
- **resume_condition**: Supervisor 调整 Mission 将 personal/CUA safety 重新纳入 scope；或其 contextual-integrity / least-privilege 主题被 Agent-Facing Environment Runtime 的 verifier/affordance 实验证明为必要子问题
- **confidence**: 0.4

---

## Abandoned Directions

（暂无）

---

## Discussion Topics

### GUI Agent 研究方向优先级确认 — 2026-04-28

- **raised_by**: agenda-evolve
- **context**: 今日完成 GUI Agent 全面 survey（190 篇论文）、memory-distill（4 个新 pattern）、3 个 idea 生成与评估。Grounding Robustness (16/25) 评分最高，Credit Assignment 方向被 WebSearch 发现极拥挤（5+ concurrent works），Adversarial Verification 风险最高 (11/25)
- **question**: 当前以 GUI Grounding Robustness 为 primary direction、RL Training 为 secondary、Self-Improving 为 monitoring 的优先级分配是否合理？是否需要调整？
- **related_direction**: GUI Grounding Robustness, RL-based GUI Agent Training, Self-Improving Agent Reliability

### Credit Assignment 方向是否继续 — 2026-05-06 更新

- **raised_by**: agenda-evolve
- **context**: SOLAR-RL 和 ProxMO 已读完。ForkPoint 评估从 12/25 降至 10/25——ProxMO 的 PSA (TF-IDF state similarity → soft baseline) 概念上与 ForkPoint 的 state change detection 高度重叠，SOLAR-RL 的 first failure point detection 本质就是 fork point detection。Credit assignment 赛道已有 6+ concurrent works (SOLAR-RL, GiGPO, ProxMO, ADMIRE, DAPO, GUI-Shepherd)
- **question**: 建议暂停 credit assignment 子方向，转向 rule-based reward design（更底层、更少竞争的 RL 子方向）。是否同意？或者是否有 credit assignment 的独特角度（如 GUI-specific visual state similarity）值得继续探索？
- **related_direction**: RL-based GUI Agent Training

### SGV 论文来源 — 2026-05-07

- **raised_by**: autoresearch
- **context**: Self-Improving direction next_action 指向"阅读 SGV (Self-Grounded Verification) 论文"。Vault 中 DomainMap 提到 SGV "20pp OSWorld 提升"，但无具体 paper URL 或 arxiv ID。Web search 未返回匹配结果。UI-Genie 论文已消化，未提及 SGV 论文。
- **question**: 请提供 SGV (Self-Grounded Verification) 论文的 arxiv URL 或完整标题。如果该论文未公开发表或名称不同，请告知正确来源。
- **related_direction**: Self-Improving Agent Reliability

### Autoresearch 推进受阻 — 2026-05-19

- **raised_by**: autoresearch
- **context**: Round 2 检测到所有 active directions 均被阻塞：(1) GUI Grounding Robustness 的 next_action 是"原型验证 FPN + multi-resolution training"（需实验实现，超出 autoresearch scope）；(2) RL-based GUI Agent Training 的 next_action 需要"Supervisor 决策是否完全放弃 credit assignment"；(3) Self-Improving Agent Reliability 需要 SGV 论文 URL。同时，Queue 中有 32 个 pending papers（多为 daily-papers 产生的 summarize_paper 任务），但 WebFetch 被网络限制阻塞，无法执行 paper-digest。
- **question**: 请提供以下任一指导以解除阻塞：(1) 提供可访问的论文 PDF 或替代获取方式（绕过 WebFetch 限制）；(2) 决策 RL Training 方向是否放弃 credit assignment 转向 rule-based reward design；(3) 提供 SGV 论文来源；(4) 指示 GUI Grounding 实验实现的优先级（是否应作为 autoresearch 的行动项）。
- **related_direction**: 所有 active directions

### 新方向纳入与 Self-Improving 暂停确认 — 2026-06-25

- **raised_by**: agenda-evolve
- **context**: 6/23–6/25 围绕 agent-facing environment 与 personal CUA safety 积累了 10+ 篇 paper notes、3 篇 survey（AgentFriendlyEnvironment / ComputerUseAgents / GUI-Environment）、2 篇 report 与 4 个 idea（AgentFacing-WebRuntime 18/25、HybridVerifier-GUIRuntime 18/25、EvidenceDependence-GUIGrounding 18/25、PersonalizedSafety-CUA 20/25），但 5/19 之后 agenda 的 Active Directions 未反映这些进展。本轮 agenda-evolve 新增 "Agent-Facing Environment Runtime"（high）与 "Personal CUA Safety & Contextual Integrity"（medium），并暂停 "Self-Improving Agent Reliability"。另：5/19 "Autoresearch 推进受阻" 中的 WebFetch 阻塞已通过 scripts/lexmount_fetch.py + references/network-fetch-fallback.md 解决，paper-digest 6/24–6/25 已正常运行——该 Discussion Topic 可视为已解除。
- **question**: (1) primary direction 是否从 GUI Grounding Robustness 调整为 / 并列 Agent-Facing Environment Runtime？两者是否应合并（均以"环境/grounding 的可观测、可验证能力"为核心）还是保持独立？(2) Personal CUA Safety 是否在当前 Mission scope 内（Mission 聚焦 grounding/operating GUI 可靠性），还是应降级为 monitoring？(3) 是否确认暂停 Self-Improving Agent Reliability，并将其 verifier 主题并入 Agent-Facing Environment Runtime？
- **related_direction**: Agent-Facing Environment Runtime, Personal CUA Safety & Contextual Integrity, GUI Grounding Robustness, Self-Improving Agent Reliability
- **resolved**: 2026-06-26 Supervisor 回复 — (1) **primary = Agent-Facing Environment Runtime**（GUI Grounding 降为 secondary high，两者独立不合并，但 grounding 可观测角度并入 AFE affordance）；(2) **Personal CUA Safety 不再在 Mission scope 内** → 移入 Paused；(3) **确认暂停 Self-Improving Agent Reliability**
