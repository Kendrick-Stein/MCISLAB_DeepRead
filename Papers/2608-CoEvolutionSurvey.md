---
title: "Co-Evolution in Agentic Systems: Toward Self-Directed Evolution Beyond Human Design"
authors: [Qing Zong, Jiayu Liu, Junhao Shen, Zecong Tang, Linsi Wu, Yuxuan Liu, Rui Wang, Zhaowei Wang, Weiqi Wang, Cheng Qian, Xiusi Chen, Yangqiu Song]
institute: [HKUST, UIUC, CUHK, HKU, Peking University]
date_publish: 2026-08-10
venue: arXiv
tags: [agentic-RL, LLM]
url: "https://arxiv.org/abs/2608.10299"
arxiv_id: "2608.10299"
doi: ""
cite_key: zong2026co
code:
rating: "4"
content_scope: full-text
verification_status: source-checked
date_added: 2026-08-13
---
## Summary
这篇 HKUST/UIUC/CUHK/HKU/PKU 联合 survey 把 co-evolution（多个组件相互施加 adaptive pressure 的多组件 self-evolution）作为中心组织轴，提出渐进三阶段 taxonomy：Agent-Agent、Agent-Environment、Meta Co-Evolution。全文主线是"演化自由边界（boundary of evolutionary freedom）逐步扩大、系统逐步摆脱 human-engineered constraints"，并统一形式化为演化算子 Ω 作用域的扩张。

## Problem & Motivation
Agentic system 部署后需要持续改进，但 single-entity self-evolution 受限于 static learning context（固定的 task 与 feedback），改进曲线有上界。既有 self-evolving agents surveys（Gao et al. 2026、Xiang et al. 2026 等）以单 agent 内部组件（model / memory / tool / harness）为组织轴，只把 co-evolution 当 subtheme。本文以 co-evolution 为 central inclusion criterion，追问三个问题：哪些组件在共演、演化自由边界如何跨组件扩张、这一过程的终极形态是什么。

## Method
**形式化框架（Sec. 2）**：系统 S=(A,E)，每个 agent a_i=(m_i, h_i) 由 model backbone 与 harness 构成，A=({a_1..a_n}, Π) 中 Π 编码角色与通信拓扑。演化以算子 S^(t+1)=Ω(S^t, τ^t) 描述，Ω 规定 what/when/how/where evolve 与质量评估方式。co-evolution 的判别标准：**至少两个 evolving units 相互适应并持续重塑彼此的后续演化**，仅交换信息或交互不算。Appendix A 据此与十个相邻概念逐一划界（multi-agent interaction、agent loops、harness engineering、evolutionary optimization、continual learning、self-play、self-evolution、meta-evolution、recursive self-improvement、open-endedness）。

**Stage 1 — Agent-Agent Co-Evolution（Sec. 3）**：A^(t+1)=Ω(A^t, E, τ^t)，环境 E 固定，耦合演化发生在 agent collective 内部。三类：
- *Adversarial*：pairwise（GAN、ACE-Safety 的 MCTS 搜攻击、MAGIC 多轮攻防博弈）与 multi-source（AlphaStar league training、TriPlay-RL 攻击者/防御者/评估者三方共演）；
- *Collaborative*：parallel（MARL、CoMAS 从讨论中生成 reward、CORAL 经共享 memory 扩散尝试与 skill）与 role-differentiated（CORY 先答后改、CoVerRL 从多数投票自举 verifier、EvoScientist 研究者/工程师双角色积累经验）；
- *Evolving organizations*：角色与团队结构本身可演化（R3DM 从行为中发现角色、SkillMAS 联合更新 skill 与团队结构）。

**Stage 2 — Agent-Environment Co-Evolution（Sec. 4）**：(A^(t+1), E^(t+1))=Ω(A^t, E^t, τ^t)，环境状态进入更新，按被演化的子空间分三类：
- *Task-space*：exposure/selection（curriculum、PORTAL 选中间任务）与 adaptive generation（GenEnv 难度对齐共演、Tool-R0 按 solver 成功率校准难度、Search Self-Play 生成 multi-hop 可验证问题）；
- *Feedback-space*：preference-driven（PEBBLE、DUO 挑 reward 分歧大的样本对）、outcome-driven（ROSKA 共搜 reward 候选与 policy 变体、CURE 从执行失败演化 unit test）、consistency-augmented（ARCO 步级分数与最终结果对账、ECHO 按建议是否改进 policy 更新 critic）；
- *Interaction-space*：executable world construction（POET 演化 environment-agent pair 种群、OpenAI ADR 随 policy 变强扩大随机化范围、LLM-POET）与 model-based world construction（WebEvolver 共训 web world model 与 agent policy、COMAP on-policy 文本 world model、EvolvingAgent）。

**Stage 3 — Meta Co-Evolution（Sec. 5）**：Ω^(t+1)=Γ^t(S^t, Ω^t, τ^t)，下层共演系统通过自生成的 revision process Γ 修订演化机制本身。作者明确指出现有多数工作只是 single-entity precursor（PromptBreeder 演化 mutation prompt、MemEvolve 演化 memory 架构）；更接近 true meta co-evolution 的例子仅 RQGM 一类——在 task agents 与 evaluators 共演之上，meta-agent 利用 joint feedback 引导后续演化。

## Key Results
本文是 survey，无自有实验；核心产出为 taxonomy 与两项 survey 层面的证据整理：
- **Figure 4 cross-paper evidence**：汇总被综述论文的结果论证 co-evolution 的 effect / consistency / convergence——Panel A/B 为各论文内部 static-vs-evolving 的 matched 对比（均值/配对提升），Panel C 为归一化 performance 轨迹；数据选取与聚合方法在 Appendix C 说明。
- **Appendix B Table 1** 与 Gao et al. 2026、Xiang et al. 2026（self-evolving agents surveys）、Guo et al. 2024（LLM multi-agent survey）等逐项对比，声称的差异是它们均未以 co-evolution 为中心轴。
- **挑战三条**（Sec. 6）：dynamic evaluation（固定 benchmark 需辅以 historical cross-play、component ablations、held-out evaluators 等过程级测试）；scaling（agents/harness/environment 联动更新时决定"谁变、更新如何互相影响、如何保持演化压力 productive 而非 unstable"）；safety & governance（演化出的攻击策略与通信协议可能超出人类理解，需 sandboxed deployment、continuous monitoring、rollback to verified states、human intervention points）。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | 首个以 co-evolution 为中心组织轴的 agentic systems survey；既有 self-evolving surveys 只把它当 subtheme | sota-novelty | Sec. 1; Appendix B | "Surveys on self-evolving agents (Gao et al., 2026; Xiang et al., 2026) are closest to our scope, but treat co-evolution as a subtheme" | source-verified |
| C2 | Stage 1 定义：A^(t+1)=Ω(A^t,E,τ^t)，E 固定，耦合在 agent collective 内部 | causal-mechanism | Sec. 2.3; Sec. 3 | "A^{t+1}=Ω(A^t, E, τ^t)"; "mutual adaptation among evolving peers within a fixed environment" | source-verified |
| C3 | Stage 2 定义：(A^(t+1),E^(t+1))=Ω(A^t,E^t,τ^t)，环境进入更新，分 task/feedback/interaction 三子空间 | causal-mechanism | Sec. 2.3; Sec. 4 | "(A^{t+1},E^{t+1})=Ω(A^t, E^t, τ^t)"; "extends the process to the environment itself" | source-verified |
| C4 | Stage 3 定义：Ω^(t+1)=Γ^t(S^t,Ω^t,τ^t)，演化机制由自生成 revision process 修订 | causal-mechanism | Sec. 2.3; Sec. 5 | "revises its evolution mechanism through a self-generated revision process Γ^t: Ω^{t+1}=Γ^t(S^t,Ω^t,τ^t)" | source-verified |
| C5 | co-evolution 判别标准：≥2 个 evolving units 相互重塑彼此后续演化；Appendix A 与十个相邻概念划界 | comparison | Sec. 2.2; Appendix A | "at least two evolving units jointly adapt and continually reshape each other's further evolution, rather than merely exchanging information or interacting" | source-verified |
| C6 | Appendix B 对比对象含 Gao et al. 2026、Xiang et al. 2026、Guo et al. 2024 等，差异为中心轴不同 | comparison | Appendix B, Table 1 | "we use co-evolution as the central inclusion criterion" | source-verified |
| C7 | 归类：AlphaStar → multi-source adversarial；POET/ADR → executable world construction；WebEvolver → model-based world construction | comparison | Sec. 3.1.2; 4.3.1; 4.3.2 | "AlphaStar…league training"; "POET…evolves a population of environment-agent pairs"; "WebEvolver…co-trains a web world model with the agent policy" | source-verified |
| C8 | PromptBreeder/MemEvolve 被归为 single-entity precursors；RQGM 被作为更接近 true meta co-evolution 的例子 | comparison | Sec. 5.2 | "Most related methods remain single-entity precursors… RQGM (Iacob et al., 2026) goes beyond by co-evolving task agents and evaluators" | source-verified |
| C9 | Figure 4 汇总跨论文证据（Panel A/B matched 对比、Panel C 归一化轨迹），构建方法见 Appendix C | benchmark-setting | Figure 4; Appendix C | "Cross-paper evidence for the effect, consistency, and convergence of co-evolution. See Appendix C for data selection and aggregation details." | source-verified |
| C10 | 论文未提供本 survey 自己的 centralized GitHub repo / paper-list 链接 | license-code | abs 页 + 全文检索 | —（verifier 全文与 abs 页检索均无本 survey 的 repo 链接） | source-verified |

## Strengths & Weaknesses
**亮点**：
- 以"演化算子 Ω 作用域扩张"为轴的渐进 taxonomy，比按组件罗列的 self-evolution survey 更有判别力——它自带明确的 inclusion criterion（mutual adaptive pressure），Appendix A 的十项概念划界直接回应了该领域 self-play / open-endedness / meta-evolution 术语混用的问题。
- Figure 4 的 cross-paper evidence 汇总（static-vs-evolving matched 对比 + 归一化轨迹）在 survey 中少见，是"survey 也应给证据"的好实践。
- 对 Stage 3 保持诚实：作者明确承认现有工作绝大多数只是 single-entity precursor，真正的 meta co-evolution 例证极薄。

**局限**：
- Stage 3 实质上只有 RQGM 一个像样例子，"三阶段"中的第三阶段更接近 aspiration 而非成熟文献簇；taxonomy 的渐进叙事隐含"演化自由更大 = 更接近终极形态"的方向性预设，而 Sec. 6 的 safety 讨论自己也承认更大自由带来失控风险——两者之间的张力文中未正面处理（推测性评价）。
- Figure 4 的跨论文汇总受各论文 benchmark、setting 差异限制，Appendix C 的 data selection 本身可能引入幸存者偏差（作者未报告失败/负面案例的纳入比例；推测）。
- 三条挑战（evaluation / scaling / safety）停在方向性建议，未给出可操作的评测协议或 governance 机制设计。

## Mind Map
```mermaid
mindmap
  root((CoEvolutionSurvey))
    Problem
      单实体 self-evolution 受 static context 上界
      既有 survey 把 co-evolution 当 subtheme
    Method
      形式化 S=(A,E), 算子 Ω
      Stage 1 Agent-Agent
        Adversarial / Collaborative / Organizations
      Stage 2 Agent-Environment
        Task / Feedback / Interaction space
      Stage 3 Meta
        Ω 自身可演化, Γ revision
    Results
      Figure 4 cross-paper evidence
      Appendix B 对比既有 survey
      挑战: evaluation / scaling / safety
```

## Notes
- 与 vault 已有 [[2507-SelfEvolvingAgentsSurvey]]、[[2508-SelfEvolvingAIAgentsSurvey]] 正交互补：那两篇以单 agent 内部组件为轴，本篇以多组件耦合为轴；三篇合看可覆盖 self-evolution 文献的两种切法。
- Stage 2 的 task-space / interaction-space 分类与近期消化的 environment-evolution 工作（EnvACE、EvoHarnessRL 一类）直接相关，可作为该方向的定位地图；GUI agent 的环境/harness 共演问题在本文框架下属于 Stage 2 interaction-space + harness 演化的交叉，文中覆盖较少，或是空白点。
