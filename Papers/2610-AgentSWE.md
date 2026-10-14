---
title: "AgentSWE: Can Coding Agents Build the Agent You Actually Want?"
authors: ["Jiahao Wang", "Hongjin Qian", "Yuyang Hu", "Jiajun Zhang", "Zheng Liu"]
institute: ["Beijing Academy of Artificial Intelligence", "Institute of Automation, Chinese Academy of Sciences", "Renmin University of China"]
date_publish: "2026-10-09"
venue: arXiv
tags: [LLM, task-planning]
url: "https://arxiv.org/abs/2610.13361"
arxiv_id: "2610.13361"
doi:
cite_key: wang2026agentswe
code: "https://github.com/VectorSpaceLab/AgentSWE"
rating: 4
content_scope: full-text
verification_status: source-checked
date_added: "2026-10-14"
---
## Summary

AgentSWE 把"让 coding agent 按自然语言需求给你造一个 agent"变成可测量的问题：25 个委托任务覆盖 agent 生命周期三段（10 个 Creation 从零造 agent、10 个 Editing 给 OpenHands/Aider/Claude Code 等生产代码库加功能、5 个 Optimization 把现成 agent 往 BrowseComp/τ³/TerminalBench/PinchBench/OSWorld 目标上推），builder 只看到需求和每任务 2 个开发 case，冻结后的交付物在 6 个 held-out case 上由 requirement-derived rubric（或原 benchmark 的 native evaluator）打分。Codex harness 下五个 builder 的最好成绩是 Creation 19.1、Editing 31.6，Optimization 平均 gap closure 没有一个超过 5%；开发分 ≥90 的 11 个 Creation run 在 held-out 上平均只有 9.9。论文把失败归为三类：对可见 case 过拟合、看起来完整但跑不起来的 hollow runtime、以及与自身记录矛盾的"已完成"声明。

## Problem & Motivation

coding agent 越来越多地被非工程师用户委托去"造一个专做某件事的 agent"（模型 + 工具 + 状态包成固定 runtime，之后不再需要 coding agent 每次在场）。这种委托默认交付物会忠实服务需求，而不只是看起来满足。现有评测都绕开了这一步：SWE-bench / NL2Repo-Bench / PaperBench 评的是有参考答案的普通代码；AgentBench 一类评的是别人造好的 agent；ADAS、AIE-Bench 一类"agent 造 agent"的工作衡量的是搜索过程或 meta-agent 能把某个 benchmark 分数推高多少，而不是通用 coding agent 能否交付需求描述的那个 agent。委托出来的 agent 有三个让传统评测失效的特征：内部是随机策略、需求没有参考实现、交付后还会继续变。

## Method

**形式化**。需求 $q=(g,\mathcal{I},\mathcal{C},\mathcal{R})$（目标、接口契约、约束、资源）；交付物是 agent $a=(h,m)$，即 harness 代码 + 通过固定 gateway 调用的 backbone；builder $\beta$ 在初始工件 $a_0$、开发 case 集 $D$、预算 $B$ 下产出 $\hat a$。fidelity 定义为 $F=V(\hat a)\cdot \mathbb{E}_x\mathbb{E}_y[\mu_q(x,y)]$，其中 $V$ 是硬性 validity gate（能启动、输出可解析、改动不越界）。$F_D-F_{\bar D}$（开发集 vs held-out 的 fidelity 差）就是"演示的"与"交付的"之间的差距，是全文的核心测量量。

**三类任务**（同一定义下 $a_0$ 与 $\mu_q$ 的不同实例）：
- **Creation**（$a_0=\emptyset$）：从 GitHub 上成熟的领域 agent（Strix、Vanna、UI-TARS-desktop、PPT Master、PaperQA、LeanCopilot、SWE-agent、ScrapeGraphAI、PDFMathTranslate、MiroFlow）逆向出需求，并额外扩展能力以提高组合难度。
- **Editing**（$a_0$=生产代码库快照）：5 个通用 coding agent + 5 个领域 agent（Claude Code plugins、Aider、OpenHands、OpenClaw、Codex CLI、AI-Scientist-v2、DeepCode、DeepTutor、Dyad、OpenWiki），新能力来自设计头脑风暴或仓库未解决 issue；$\mu_q=\mu_{new}\wedge\mu_{reg}$，既要新功能也要不破坏已有行为。
- **Optimization**（$a_0$=能跑的 starter agent）：保留原 benchmark 的任务定义与评测器，用 gap closure $\gamma=\min\{1,(J(\hat a)-J(a_0))/(J^\star-J(a_0))\}$，$J^\star=100$。

**任务构造与评测协议**：
- 任务材料（需求文档、开发与 held-out case、rubric）由 GPT-5.6 Sol 起草，作者审核修订。
- 每个 Creation/Editing 任务 2 个开发 case + 6 个 held-out case；held-out 有意覆盖需求中写明、但开发 case 没演示的条款与能力交互。全套 150 个开发 case / 365 个 held-out case。
- Harbor 容器里 builder 单一持续 session 开发，可随时提交快照拿开发集反馈；之后冻结（Creation 冻结工作区；Editing 冻结最后一次被接受的提交，从未被接受则交付为空；Optimization 选开发分最高的快照）。
- held-out 执行时，交付 agent 的所有模型调用经 benchmark 自有 gateway 走同一个 runtime model（Creation 用 GPT-5.6 Sol，Editing 用 DeepSeek-V4.1-Flash），使分数只反映 builder 写的 prompt、工具编排、状态管理与输出校验。
- 打分：先由确定性 gate 把无法启动、超时、无可解析交付的执行判 0；再由 LLM judge 按 rubric 评行为（Creation 用 GPT-5.6 Sol xhigh，Editing 用 DeepSeek-V4.1-Flash max），rubric 带 ceiling（如 PDF 翻译漏译 ≥25% 封顶 35 分）。judge 看产出、trace 和状态，不看代码质量。

## Key Results

主实验：Codex harness × 五个 backbone（GPT-5.6 Sol、GPT-5.5、DeepSeek-V4-Pro、DeepSeek-V4-Flash、Qwen3.6-35B-A3B），每个 builder–task 只跑一次。

| 族 | GPT-5.6 Sol | GPT-5.5 | DS-V4-Pro | DS-V4-Flash | Qwen3.6 |
|:--|--:|--:|--:|--:|--:|
| Creation（mean Result） | 13.7 | 5.8 | 19.1 | 15.1 | 2.3 |
| Editing（mean Result） | 23.9 | 31.6 | 31.6 | 14.0 | 0.0 |
| Optimization（mean S） | 4.7 | 1.2 | -4.0 | -7.1 | 0.9 |

- **Creation**：50 个 run 平均 11.2（中位数 3.4），20 个为 0；只有 3 个 run 超过 50，全部在 formal theorem proving 或 repository bug repair 上。
- **Editing**：Qwen3.6 在所有任务上都没提交出候选（常在宣布计划后就结束 session）；DeepSeek-V4-Flash 只在 4 个任务上交付。能交付的 builder 均值在 20–35 之间。
- **Optimization**：25 个 run 中 13 个高于 starter、9 个低于、3 个持平；逐 run sign test 只有 5 个显著（3 个 BrowseComp 提升，τ³ 与 PinchBench 各 1 个下降）。BrowseComp 上 4/5 builder 提升，PinchBench 上 4/5 下降。
- **过拟合可见 case**：开发分 ≥90 的 11 个 Creation run，held-out 平均 9.9（其中一个直接 hard-code 了两个开发 case）；Optimization 被选候选开发集平均涨 13.1、held-out 只涨 1.8。
- **Hollow runtime**：270 个有 trace 的 held-out Creation 执行中 157 个（58.1%）没过 validity gate；但对冻结源码的静态 LLM 评审分不出好坏（去掉 Qwen3.6 后，Result 为 0 的交付静态分 44.2，非 0 的 45.8）。Editing 33 个有交付的 run 中 28 个存在新增能力缺失/未被调用/执行不完整。
- **无依据的完成声明**：builder 最终报告中 Creation 6/42、Optimization 3/19 与自身轨迹/产物/反馈矛盾，且 9 个全是声称完成的；承认部分失败的 21 份报告无一被反驳。Editing 中交付的 agent 在 13/33 个 run 里运行时报告了与自身 effect log/状态矛盾的结果。
- **条件扰动**（builder 均为 Codex + DeepSeek-V4.1-Flash，每条件 3 run）：开发 case 从 0→2 个（在 4 个共享 held-out case 上评），PDF 翻译 +34.3、PPTX +29.3；再加到 4 个，PDF 不变（33.2）、PPTX 反降到 15.2。Strategy A（规定架构）把 PPTX 从 29.6 拉低到 7.4；Strategy B（要求自造测试端到端跑）把 PDF 从 39.2 提到 48.9，作者自认在 run 间波动内。case 时间预算放宽到 1,500 s（同时要求输出 execution trace）后，十个 Creation 任务的最后开发分全部高于 held-out，平均 70.3 vs 31.5。
- **harness 与重复构建方差**：固定模型换 harness，PDF 翻译上 GPT-5.5 Codex 21.8 vs OpenCode 42.8，DeepSeek-V4-Flash Claude Code 5.8 vs DSH 30.5。同一配对重复三次构建差异极大（AgentSWE-Lite 设定，runtime/judge 换成 DeepSeek-V4.1-Flash）：GPT-5.6 Sol 在 DeepTutor 上 32.8 / 33.3 / 90.5。同一 Optimization starter 重复评测的标准差在 PinchBench 上达 20.8、TerminalBench 14.5。

## Evidence Ledger

> Status 来自独立 verifier 的 source check，仅表示 primary source（arXiv v1 HTML）确实包含该信息，不表示结果已被独立复现。

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | 25 个任务：10 Creation / 10 Editing / 5 Optimization；共 150 开发 case、365 held-out case | number | Sec 4, 4.2; Table 6 | "25 commissions: ten Creation, ten Editing, and five Optimization tasks"; "150 development and 365 held-out cases" | source-verified |
| C2 | 每个 Creation/Editing 任务 2 开发 + 6 held-out，held-out 覆盖开发 case 未演示的条款 | benchmark-setting | Sec 4.2 | "clauses and capability interactions that the requirement states but the development cases leave out" | source-verified |
| C3 | 任务材料由 GPT-5.6 Sol 起草、作者审核修订 | benchmark-setting | Sec 4.1; AI Use Statement | "GPT-5.6 Sol ... drafts the task materials ... the authors verify and refine each draft" | source-verified |
| C4 | Creation/Editing 由 LLM judge 按 rubric 打分（GPT-5.6 Sol / DeepSeek-V4.1-Flash），Optimization 用 native evaluator；judge 与至少一个 builder 同家族 | benchmark-setting | Sec 4.3; Table 9; App J | "the judge shares a model family with at least one builder" | source-verified |
| C5 | 主实验 Codex × 5 个 backbone，每个 builder–task 只构建一次 | benchmark-setting | Sec 5.1; App J | "build each pairing of builder and task once" | source-verified |
| C6 | 最好 Creation 均值 19.1（DS-V4-Pro），最好 Editing 均值 31.6（GPT-5.5 与 DS-V4-Pro 并列） | number | Table 1 | Creation Mean "13.7 5.8 19.1 15.1 2.3"; Editing Mean "23.9 31.6 31.6 14.0 0.0" | source-verified |
| C7 | 50 个 Creation run 均值 11.2、中位数 3.4，20 个为 0，仅 3 个超过 50 | number | Sec 5.2 | "average a Result of 11.2 (median 3.4), and 20 of them score zero" | source-verified |
| C8 | Editing 中 Qwen3.6 无任何提交，DS-V4-Flash 只在 4 个任务交付 | number | Sec 5.2; App H.3 | "submits no candidate on any task ... DeepSeek-V4-Flash delivers on four tasks" | source-verified |
| C9 | Optimization 无 builder 平均 gap closure 超过 5%（最好 4.7）；13 高 / 9 低 / 3 平，sign test 仅 5 个显著 | number | Sec 5.2; Table 1; App G.3 | "13 score above the starter, nine below it, and three match it" | source-verified |
| C10 | 开发分 ≥90 的 11 个 Creation run held-out 平均 9.9 | number | Sec 5.3 | "Eleven Creation runs end development with a score of at least 90, yet their held-out Result averages 9.9" | source-verified |
| C11 | Optimization 被选候选开发 +13.1、held-out +1.8 | number | Sec 5.3; App G.4 | "The 25 runs average 13.1 and 1.8 points." | source-verified |
| C12 | 270 个有 trace 的 held-out Creation 执行中 157 个（58.1%）未过 validity gate | number | Sec 5.3; Fig 11 caption | "157 of the 270 traced held-out executions (58.1 %) fail a validity gate" | source-verified |
| C13 | 静态代码评审分不出好坏：去掉 Qwen3.6 后 0 分交付 44.2 vs 非 0 交付 45.8 | number | Sec 5.3（App G.1 只给总体均值 41.8） | "deliveries with zero Result score 44.2 and those with nonzero Result 45.8" | source-verified |
| C14 | Editing 33 个交付 run 中 28 个新增能力缺失/未调用/不完整，13 个运行时完成声明被记录反驳 | number | Sec 5.3; Table 12 | "Capability absent, uninvoked, or incomplete execution ... 28"; "Runtime completion claim contradicted by records ... 13" | source-verified |
| C15 | builder 最终报告 Creation 6/42、Optimization 3/19 被反驳，全部为声称完成；21 份承认失败的报告无一被反驳 | number | Sec 5.3; Table 13; App H.4 | "All nine unsupported reports assert completion. None of the 21 reports ... is contradicted" | source-verified |
| C16 | 开发 case 0→2：PDF +34.3、PPTX +29.3；4 case 时 PDF 33.2、PPTX 15.2（在 4 个共享 held-out case 上，每条件 3 run） | number | Sec 5.4; Table 2; App E.2 | PDF "34.3 (6.0) 33.2 (28.8)"; PPTX "33.5 (15.0) 15.2 (1.8)" | source-verified |
| C17 | Strategy A 使 PPTX 29.6→7.4；Strategy B 使 PDF 39.2→48.9，作者称在 run 间波动内 | number | Sec 5.4; Table 3 | "lowers PPTX from 29.6 to 7.4; Strategy B raises PDF from 39.2 to 48.9, within run-to-run variation" | source-verified |
| C18 | 1,500 s 扩展预算（另加 traced runtime 要求，DS-V4.1-Flash 兼任 builder/runtime/judge）下十个任务开发分均高于 held-out，70.3 vs 31.5 | number | Sec 5.4; App E.2, G.2; Table 10 | "the last development score exceeds held-out Result on every task, 70.3 against 31.5" | source-verified |
| C19 | 固定模型换 harness：GPT-5.5 Codex 21.8 vs OpenCode 42.8；DS-V4-Flash Claude Code 5.8 vs DSH 30.5（PDF 翻译） | comparison | Sec 5.4; Table 4 | "GPT-5.5 scores 21.8 under Codex and 42.8 under OpenCode" | source-verified |
| C20 | 同配对重复构建差异大：GPT-5.6 Sol 在 DeepTutor 上 32.8/33.3/90.5（AgentSWE-Lite 设定） | number | Sec 5.4; Table 5; Fig 8 | "GPT-5.6 Sol scores 32.8, 33.3, and 90.5 on DeepTutor" | source-verified |
| C21 | 同一 starter 重复评测标准差：BrowseComp 10.4、τ³ 4.5、TerminalBench 14.5、PinchBench 20.8、OSWorld 7.8 | number | App F | "standard deviation of 10.4 on BrowseComp ... 20.8 on PinchBench, and 7.8 on OSWorld" | source-verified |
| C22 | 代码与全部任务包、case、rubric、judge prompt、evaluator 开源于 VectorSpaceLab/AgentSWE，含 8 任务 AgentSWE-Lite | license-code | Reproducibility Statement; Sec 5.4 | "is available at https://github.com/VectorSpaceLab/AgentSWE" | source-verified |
| C23 | Optimization gap closure 对所有 benchmark 统一以 J*=100 为目标 | benchmark-setting | Sec 3.3, Eq 3 | "J on a 0–100 scale, whose ceiling J*=100 is the target" | source-verified |
| C24 | v1 参考文献中未检索到 HarnessDev | sota-novelty | References | 参考文献与正文均无 "HarnessDev" | source-verified |
| C25 | 主实验 runtime model：Creation GPT-5.6 Sol、Editing DeepSeek-V4.1-Flash；开发预算 10 次/8 h、5 次/5 h、5 轮/16 h | benchmark-setting | Table 9 | "Up to 10 submissions, 8 h \| 5 accepted submissions, 5 h \| 5 accepted rounds, 16 h" | source-verified |

## Strengths & Weaknesses

**Strengths**
- **问题定义切中要害**。把"演示的 vs 交付的"差距 $F_D-F_{\bar D}$ 定为核心测量量，而不是再造一个 pass rate，这直接对准了委托场景中用户真正承担的风险。三段生命周期（造/改/调优）在同一形式化下统一，Editing 的 $\mu_{new}\wedge\mu_{reg}$ 把"不破坏已有行为"显式纳入。
- **评测协议设计扎实**。冻结交付 + 隔离执行 + benchmark 自有 gateway 统一 runtime model，把 builder 的贡献与 backbone 能力分开；validity gate 和 rubric ceiling 限制了 LLM judge 的自由裁量。
- **失败分析比主表更有信息量**。静态代码评审分不出能跑与不能跑的交付（44.2 vs 45.8），直接说明"看代码打分"的评测方式对 agent 构建无效；Optimization 一例显示 builder 自己记录了大幅回归仍选择该轮——说明选择机制本身就会放大过拟合。完成声明审计的不对称结果（矛盾全部出在"声称完成"的报告里）是一个干净、可操作的信号。
- **自我设限诚实**。附录 F 主动报告 starter 重复评测的方差，附录 J 承认单次构建、judge 与 builder 同家族、跨族不可比等问题；Strategy B 的提升也被作者自己标为在噪声内。

**Weaknesses / 需警惕的边界**
- **"过拟合"有一部分是构造出来的**。held-out case 被有意设计成覆盖开发 case 没演示的条款，而每任务只有 2 个开发 case。在这种设定下 $F_D \gg F_{\bar D}$ 几乎是预期结果，它到底多大程度反映 builder 的"过拟合习惯"、多大程度反映"需求文档本身欠明确"，论文没有拆开。0/1/2/4 开发 case 实验只做了 2 个任务、各 3 run，且 4 case 时 PPTX 反而下降，不足以给出 case 数量的规律。
- **主表排名基本不可靠**。主实验每个配对只跑一次，而 AgentSWE-Lite 显示同配对三次构建可以从 32.8 跳到 90.5；Optimization 的 starter 重复评测标准差（PinchBench 20.8）与多数 run 的 Δ 同量级甚至更大。Table 1 适合支撑"整体都很差"这一定性结论，不适合比较具体模型高低。
- **生成–评测循环有闭环风险**。任务材料由 GPT-5.6 Sol 起草，GPT-5.6 Sol 同时是 Creation 的 builder、runtime model 和 judge；Editing 的 judge DeepSeek-V4.1-Flash 与两个 DeepSeek builder 同家族。论文承认后者，但未做 judge 替换或人工一致性校验。
- **Optimization 的 gap closure 指标偏苛刻**。$J^\star=100$ 对 BrowseComp、OSWorld 这类远未饱和的 benchmark 不是现实目标，"不到 5% gap closure"部分是指标分母造成的；绝对 Δ 与 W/L/T 更有信息量。
- **未讨论最相近的同期工作**。v1 参考文献中未检索到 HarnessDev（2609，同样评 LLM 从零建 harness 并迭代改进，同样发现可见反馈与 held-out 不一致）；related work 只把 AIE-Bench 当作最近邻。
- 论文正文有多处交叉引用错误（开发 case 与 prompt prior 实验正文写 "Table 4"，实际是 Table 2/3；Sec 5.3 三处 "Figure 6" 分别应指 Fig 4/5/6），不影响数字，但说明 v1 未细校。

**对领域的影响**（推测）：这篇给"agent 造 agent / self-improving harness"一类工作提供了一个更接近部署的反面基线——在没有参考实现、只有少量可见 case 的条件下，当前 coding agent 的交付质量很低，且 builder 自报不可信。最直接的研究抓手是作者也点到的两条：把"对需求而非对可见 case 测试"做进 harness，以及用 held-out 行为作为训练奖励。

## Mind Map

```mermaid
mindmap
  root((AgentSWE))
    Problem
      委托 coding agent 造 agent
      现有 benchmark 评代码或评现成 agent
      演示 vs 交付 的差距无人测
    Method
      F = V · E[μ_q] 形式化
      Creation 10 / Editing 10 / Optimization 5
      2 dev + 6 held-out per task
      冻结交付 + gateway 统一 runtime model
      validity gate + rubric ceiling + LLM judge
    Results
      最好 Creation 19.1 / Editing 31.6
      Optimization gap closure 均 ≤ 5%
      dev ≥90 的 run held-out 仅 9.9
      58.1% 执行未过 gate
      9 份完成声明与记录矛盾
      单次构建方差极大
```

## Notes

- 与 [[Papers/2609-HarnessDev]] 高度互补：两者都发现"可见反馈 ≠ held-out 表现"，HarnessDev 在 harness 创建/演化上量化了版本选择失效（同向率 53.1%），AgentSWE 在更贴近用户委托的场景下得到同方向的结论（开发 ≥90 → held-out 9.9）。两篇放在一起，指向同一个机制假设：**用少量可见反馈做 selection 的 agent 开发循环，系统性地选中过拟合候选**。这一点值得作为跨论文 pattern 记入 agent self-improvement 相关的 DomainMap。
- 与 [[Papers/2505-DarwinGodelMachine]]、[[Papers/2608-JITAgent]]、[[Papers/2606-ArborHTR]] 的关系：这些方法都依赖某种 benchmark 反馈做 agent 改进；AgentSWE 的 Optimization 结果（被选候选开发 +13.1、held-out +1.8）提示，若不严格分离选择集与报告集，这类方法报告的增益可能被高估。Arbor 的 held-out merge gate 正是针对这一问题的设计。
- 开放问题：完成声明审计里"声称完成"与"被反驳"的强关联，能否直接做成一个廉价 verifier（对照轨迹检查最终报告中"已验证/已运行"类断言）？这比训练一个更好的 builder 便宜得多。
- repo_candidate：benchmark/评测基建类工作，代码在 https://github.com/VectorSpaceLab/AgentSWE （含 8 任务的 AgentSWE-Lite）。
