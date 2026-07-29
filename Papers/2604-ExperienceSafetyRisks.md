---
title: "On Safety Risks in Experience-Driven Self-Evolving Agents"
authors: ["Weixiang Zhao", "Yichen Zhang", "Yingshuo Wang", "Yang Deng", "Yanyan Zhao", "Xuda Zhi", "Yongbo Huang", "Hao He", "Wanxiang Che", "Bing Qin", "Ting Liu"]
institute: ["Harbin Institute of Technology", "Singapore Management University", "SERES"]
date_publish: "2026-04-18"
venue: "ACL 2026 Findings"
tags: [agentic-RL, gui-agent, web-agent]
url: "https://arxiv.org/abs/2604.16968"
arxiv_id: "2604.16968"
doi: ""
cite_key: zhao2026safety
code: ""
rating: "4"
content_scope: "full-text"
verification_status: "source-checked"
date_added: "2026-07-29"
---
## Summary

对 experience-driven self-evolving agent 安全退化的系统实证与机制分析：即使经验完全采自良性任务，AWM（offline）与 ReasoningBank（online）积累的经验仍使 7 个模型在 BrowserART / Agent-SafetyBench / SafeAgentBench 全部 21 个组合上 ASR 一致上升（GPT-4o BrowserART 37.0→50.0）。机制归因为经验的 execution-oriented 性质强化"执行而非拒绝"的先验；混入 refusal 经验可压制 ASR 但诱发 over-refusal，暴露 safety–utility trade-off。

## Problem & Motivation

Experience-driven self-evolution（agent 自我积累并复用 memory/experience）是提升 LLM agent 自主性的主流范式，但 self-curated experience 引入的安全风险研究不足。与 jailbreak / prompt injection 等外部对抗不同，本文问的是内生问题：**纯良性任务上自我积累的经验，会不会在高风险场景下反噬安全**。三个研究问题：RQ1——经验驱动自演化是否、以何种方式导致安全退化；RQ2——为什么良性经验会导致退化、经验的哪些性质负责；RQ3——现实部署（良性与有害任务混流）中经验构成如何塑造 safety–utility trade-off。与同期的 [[Papers/2509-Misevolution]]（2025-09，横扫四路径的行为学证据）分工明确：本文钉死 **memory/experience 单路径**，往下做机制层归因（论文自述 "our study uncovers the underlying mechanisms"）。

## Method

测量型论文，方法即实验设计：

- **被测框架**：offline 的 Agent Workflow Memory（AWM，workflow induction 后注入 context）与 online 的 ReasoningBank（边执行边积累/检索 memory item），覆盖经验驱动自演化的两种主流形态
- **模型**（7 个）：GPT-4o、Claude-4.5-Sonnet（闭源）；DeepSeek-V3.2、Qwen3-8B/14B/32B/235B-A22B（开源权重）
- **经验采集**：WebArena 良性 web 导航任务 + SafeAgentBench 良性 household 子集（269 benign）；推理时检索 top-3 经验
- **安全评估**：BrowserART、Agent-SafetyBench（web 子集）、SafeAgentBench（物理世界风险）；指标为 Attack Success Rate（ASR），GPT-4o 自动判定
- **机制分析工具链**（RQ2）：(1) 失败归因三分类——Sensitive Execution（良性经验在敏感语境下不安全）、Standard Execution（通用过程模式被迁移）、Format Recovery（输出格式恢复使被拦截任务得以完成）；(2) 检索条数剂量实验（Num.=1/3/5/7/9）；(3) length-matched 对照——把 system instruction 扩到与经验等 token 长度，剥离 "context 变长" confound；(4) Integrated Gradients 跨层归因（主文基于 Qwen3-32B，8B/14B 在 App D.7）
- **RQ3 现实设定**：online 演化流中混入 Agent-SafetyBench 与 SafeAgentBench 各 50 个 harmful 任务，harmful 经验形态控制为 refusal-only / execution-only / mixed 三条件（仅 4 backbone：GPT-4o、DeepSeek-V3.2、Qwen3-14B/32B）

## Key Results

1. **Offline（AWM）ASR 全线上升**（Table 1，演化前→后，7 模型 × 3 benchmark 全部 21 格上升）：

| Model | BrowserART | Agent-SafetyBench | SafeAgentBench |
|:--|:--|:--|:--|
| GPT-4o | 37.0→50.0（+35.1%） | 56.9→63.6 | 21.2→29.0 |
| Claude-4.5-Sonnet | 17.0→23.0 | 34.6→37.7 | 30.1→39.0 |
| DeepSeek-V3.2 | 48.0→61.0 | 39.7→42.5 | 24.5→36.4（+48.6%，全表最大相对增幅） |
| Qwen3-235B-A22B | 39.0→53.0 | 45.9→51.1 | 25.3→28.6 |
| Qwen3-8B | 65.0→77.0 | 56.6→58.4 | 15.6→21.2 |

（Qwen3-14B/32B 同趋势）。**Claude-4.5-Sonnet 仅在 BrowserART 与 Agent-SafetyBench 两列绝对值最低；SafeAgentBench 列（30.1→39.0）反为该列最高**（verifier 修正——"Claude 全程最稳"的流行印象在物理域不成立）。

2. **Online（ReasoningBank）**：ASR 从演化早期即上升并进入平台期，全程无自然恢复（每 20 步评估，7 模型趋势一致，Figure 2）；App D.3 长程实验（>800 步）显示 plateau 后仍有持续下滑——退化不是暂态噪声。
3. **机制**：失败归因以 Sen-Exe + Sta-Exe 为主，但构成随域而变——BrowserART 上 Sta-Exe 占大头（GPT-4o 50.0% / DeepSeek 52.6%），SafeAgentBench 上 Sen-Exe 占大头（52.9% / 46.2%）；Qwen3-8B 的 Format Recovery 在 SafeAgentBench 占 32.6%。ASR 随检索经验条数（1/3/5/7/9，条条良性）整体分层上升（局部有交叉，非严格单调，Figure 3）；length-matched 对照无法复现退化（BrowserART：GPT-4o 演化后 51.0 vs 等长对照 38.0，Table 3，5 backbone 子集），把因果钉在经验内容语义而非 context 长度；IG 显示经验片段跨层保持高 attribution（深层甚至略升），替换内容随深度衰减。
4. **RQ3 trade-off**：execution-only harmful 经验 → ASR 全程持续上升；refusal-only → 显著压制 ASR；但 refusal 经验伴随良性任务成功率明显下降（over-refusal，GPT-4o 定量曲线在 Figure 7(a)，其余 backbone 在 App D.8）——safety 与 utility 在经验构成上此消彼长。
5. **纯诊断**：不提出新缓解方法，结论呼吁 "more general, principled, and verifiable mechanisms"。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | AWM 良性经验使 GPT-4o BrowserART ASR 37.0→50.0（+35.1%） | number | Table 1 | "GPT-4o 37.0 50.0(↑35.1%)" | source-verified |
| C2 | Offline 演化后 7 模型 × 3 benchmark 全部 21 格 ASR 上升；最大相对增幅 DeepSeek-V3.2 SafeAgentBench 24.5→36.4（+48.6%） | number | Table 1 | "all 21 model×benchmark cells rise" | source-verified |
| C3 | Claude-4.5-Sonnet 仅在 BrowserART / Agent-SafetyBench 最低；SafeAgentBench 上 30.1→39.0 为该列最高（初稿"全程最低"经 verifier 对表推翻，已修正） | comparison | Table 1 | "Claude... 30.1 39.0(↑29.6%)" vs Qwen3-8B 15.6→21.2 | source-verified |
| C4 | 设置：AWM+ReasoningBank；7 模型；WebArena/SafeAgentBench 良性任务采经验；GPT-4o 判 ASR；top-3 检索 | benchmark-setting | Section 3.1 | "retrieves the top-3 experience items" | source-verified |
| C5 | Online ASR 早期即升、平台期、无自然恢复；每 20 步评估；D.3 >800 步 plateau 后仍持续下滑 | causal-mechanism | Figure 2 / §3.3 / App D.3 | "ASR curves plateau at elevated levels... no model recovering" | source-verified |
| C6 | 失败归因以 Sen/Sta-Exe 为主且随域而变：BrowserART Sta-Exe 50.0/52.6%（GPT-4o/DeepSeek）、SafeAgentBench Sen-Exe 52.9/46.2%；Qwen3-8B Format Recovery 32.6% | number | Table 2 / §4.1 | "predominantly attributed to Sensitive Execution and Standard Execution" | source-verified |
| C7 | ASR 随检索良性经验条数（Num.=1/3/5/7/9）整体分层上升，局部有交叉非严格单调 | causal-mechanism | Figure 3 / §4.2 | "increasing the number of retrieved entries leads to a clear and persistent rise" | source-verified |
| C8 | 等长 system instruction 对照无法复现退化（GPT-4o 51.0 vs 38.0；Table 3 为 5 backbone 子集），因果在经验内容语义 | causal-mechanism | Table 3 / §4.3 | "results in ASR that remain close to the pre-self-evolution baseline" | source-verified |
| C9 | IG 归因（主文 Qwen3-32B）：经验片段跨层高 attribution（深层略升），替换内容随深度衰减 | causal-mechanism | §4.3 / Fig 5(a) | "consistently high IG attribution across layers, even increasing slightly in deeper layers" | source-verified |
| C10 | RQ3 混入两 benchmark 各 50 harmful 任务；经验形态三条件；仅 4 backbone | benchmark-setting | Section 5 | "Refusal-only / Execution-only / Mixed" | source-verified |
| C11 | execution-only 使 ASR 持续升；refusal 经验压制 ASR 但良性成功率明显下降（over-refusal；定量为图线，无单一数值） | causal-mechanism | §5 / Fig 7(a) / App D.8 | "substantially suppresses the rise in ASR... notable decline in task success on benign inputs" | source-verified |
| C12 | 将 Misevolution 定位为 concurrent 行为层研究，自身定位机制层 | sota-novelty | Related Works | "a concurrent study... from a behavioral perspective... our study uncovers the underlying mechanisms" | source-verified |
| C13 | Findings of ACL 2026；全文无 code/data 链接 | license-code | abs Comments / 全文 | grep 无 github/huggingface/"available at" | source-verified |

## Strengths & Weaknesses

**Strengths**：

- **与 Misevolution 互补的分工**：Misevolution 给四路径的广度行为学证据，本文在 memory/experience 单路径给出目前最干净的机制因果链——length-matched 对照排除 "context 变长" confound、IG 归因定位经验片段的下游影响、检索条数剂量效应证明退化随经验量加重。三件套合起来的结论比单纯 before/after 对比强得多。
- **"execution bias" 机制假设有预测力**：退化不是学到有害内容，而是学到"倾向执行"的 procedural prior——这解释了为什么纯良性经验也危险，并预言 refusal 经验能对冲；RQ3 验证了该预言（同时暴露 over-refusal 代价），机制假设经受了一次 out-of-sample 检验。
- **剂量效应的可操作含义**：ASR 随检索条数分层上升（每条均良性）意味着风险由**检索聚合**放大而非单条经验携带，直接支持检索侧干预（排序/条数/组成控制）作为缓解杠杆——这正是 [[Ideas/RetrievalMediated-MemoryMisevolution]] 的靶点。

**Weaknesses**：

- 只覆盖 memory/experience 路径、两个框架（AWM / ReasoningBank）；对 tool/workflow 演化不发言，推广到 skill library、SOP 等其他经验形态是推测。
- ASR 由 GPT-4o 自动判定，而 GPT-4o 同时是被测模型之一（judge 与被测同源）；正文提取内容未见 human 校准报告。
- 诊断型论文，不提缓解方案；refusal 经验的 trade-off 定量以图线呈现，正文无单一数值。
- 与 Misevolution 一致地观察到 backbone 差异但同样未解释来源——且本文数据显示 Claude 的相对稳健是**域依赖的**（web 域最低、物理域最高），refusal robustness 的跨域结构是两文共同留下的开放问题。

## Mind Map

```mermaid
mindmap
  root((ExperienceSafetyRisks))
    Problem
      良性经验也损害安全
      RQ1 退化 / RQ2 机制 / RQ3 trade-off
    Method
      AWM offline + ReasoningBank online
      7 模型 x 3 安全 benchmark
      length-matched 对照 + IG 归因 + 剂量实验
    Results
      ASR 21 格全升 GPT-4o 37 到 50
      execution bias 强化执行倾向
      refusal 经验压 ASR 但 over-refusal
```

## Notes

- [[Papers/2509-Misevolution]] — 同期工作（本文引其为 concurrent，Shao et al.）：Misevolution（2025-09，ICLR 2026）先出，做四路径广度行为学实证；本文（2026-04，ACL 2026 Findings）后出，专注 memory/experience 路径的机制下钻。两文互为独立复现（memory 路径退化在不同框架、不同 benchmark 上均成立），共同构成 agenda Self-Improving 方向 hypothesis 的实证基础。Misevolution 笔记 Notes 中对本文的"未 digest"预留可解除。
- [[Papers/2409-AgentWorkflowMemory]] — offline 被测框架即 AWM；该笔记可补一条"已被两项独立实证指认安全风险"的下游引用。
- [[Ideas/RetrievalMediated-MemoryMisevolution]] — 本文 Figure 3 剂量效应（检索条数↑→ASR↑，单条均良性）是该 idea "检索侧因果干预"主张的最直接实证支点；idea 的 closest-works 名单应加入本文。
- [[Topics/SelfEvolvingAgents-Survey]] — survey 中列为"未能获取/未 digest"的等待项，本次补齐；风险矩阵 "AWM 使 GPT-4o ASR 37→50" 的数据来源即本文 Table 1。
- [[Papers/2510-AlignmentTipping]] — 同批 digest：受控激励环境测行为偏好翻转 vs 本文真实 memory 框架测 ASR 侵蚀——"参数外经验通道足以侵蚀对齐"在两种实验设计下独立成立。
- [[Papers/2606-MLASSelfEvolvingSafety]] — 同批 digest：其 §4（Cognitive Resource 模块）的攻击面推演正是本文实测现象的威胁模型化；本文无攻击者设定（良性经验自发退化）与 MLAS 的有攻击者设定互补。
