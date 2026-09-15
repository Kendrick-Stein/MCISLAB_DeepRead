---
title: "Prime Agent: A Self-Improving RLM Harness"
authors: ["Seth Karten", "Alex L. Zhang", "Kevin Thomas", "Sebastian Müller", "Elie Bakouch", "Daniel Auras", "Mika Senghaas", "Fares Obeid", "Konstantin Dunas", "Johannes Hagemann", "Sami Jaghouar"]
institute: ["Princeton University", "Prime Intellect", "MIT"]
date_publish: 2026-08-24
venue: arXiv
tags: [LLM, task-planning, agentic-RL]
url: "https://arxiv.org/abs/2608.23552"
arxiv_id: "2608.23552"
doi:
cite_key: karten2026prime
code: "https://github.com/PrimeIntellect-ai/prime-agent"
rating: 4
content_scope: full-text
verification_status: partial
date_added: "2026-09-09"
---
## Summary

Prime Agent 是 Prime Intellect 开源的 long-horizon agent harness，把 Recursive Language Model 的异步 `rlm` 递归调用与 Continual Harness 的版本化持久状态（prompt notes / memories / skills / subagent specifications）集成进一个带持久 IPython REPL、daemon 托管会话和 agent-to-agent 消息队列的运行时，权重不动、只改 harness 状态。核心论点是 harness 应该是"低摩擦、高表达力的膜"，不该让模型因为丢状态、限制动作、算错资源或过早终止而失败，因此把执行、恢复、验证与 root+子会话聚合计费一起标准化。评测覆盖 ARC-AGI-3、九项长上下文任务、nanoGPT speedrun、EmulatorBench、PMPP-Hard、Factorio 与 MazeBench，但 headline 的 "30% → 95.5%" 按论文 §3.1 自陈只是把结果放到外部参照旁边，并非隔离 harness 因果效应的对照实验。

## Problem & Motivation

论文的出发点是一句很干净的观察：LLM 本身没有一台计算机的完整能力。它是一个 bounded sequential processor，下一步决策只能用权重和 active context 里暴露的状态；harness 提供缺失的计算基底。但作者认为社区对 harness 的理解落后于现实——完整的信息状态早已长出 weights 和 token context 之外。

由此提出一个把 harness 当"状态缓存层级"看的框架：L0 是模型权重，L1 是 active context，L2 是持久 REPL 与递归子 agent，L3 是磁盘上的 history、memories 与 skills。四层各有独立的变更机制（L0 靠 fine-tuning，L1 靠 compaction，L3 靠 refinement），系统因此变得"more von Neumann-like"：模型可以读、变换、写当前生成指令之外的可寻址状态。

这个视角把 **expressivity** 推成 harness 的关键属性——与其编码一种固定 workflow，不如暴露原语让模型在推理时自己搭程序、子 agent 与反馈回路。第二个动机来自评测方法学：long-horizon 的主流指标是 score at fixed expenditure 或 score at practical plateau（引 METR 的 metrics of agent ability），而模型应当因为任务超出能力而失败，不该因为 harness 的工程缺陷而失败。Prime Agent 因此把自己定位成"标准化的 long-horizon 评测 harness"，而不只是一个好用的 coding agent。

## Method

**信息管理与计算管理分离。** 信息管理决定什么状态进入一次模型调用、什么在 compaction 或 restart 后存活；计算管理把模型选择的动作映射到代码、工具与递归子会话。两者由 direct agent-to-agent communication 连接，使 swarm 能动态协调而非走固定的 workflow graph。

**持久 IPython REPL（L2）。** 每个 session 拥有一个持久 REPL，安装的工具以 Python module 形式 import，用普通代码做解析、过滤、聚合与验证。中间值跨 turn 存活并停在 active context 之外，直到被显式序列化进 L1——这正是避免反复把大 log、任务规格与结构化 evaluator 输出塞回 context 的机制。L2 的变更机制被命名为 **agentic garbage collection**：模型自行创建、保留、摘要或删除 REPL 值与子 agent 会话。

**`rlm` 递归原语。** 调用 `rlm` 创建并调度一个子 agent session，在子 agent 完成前就返回一个 stable handle；子 agent 拿到自己的模型 context、IPython kernel、history 与 workspace metadata，parent 继续本地计算。结果稍后经 agent-to-agent 通信回传，保留的 handle 在 compaction 或 restart 之后仍可用于追问。论文强调它定义的是执行语义而非固定的编排图（Appendix B 给出用 `await rlm(...)` 并行 admit reviewer/tester 再用 `agent_message.send` 追加指令的完整例子），并明确"a child is a persistent concurrent session, not a stateless completion returned by rlm"。

**daemon、消息队列与 Agents View。** daemon 独立于创建它的 client 拥有 live session，root 与子 agent 共用同一生命周期（running / idle / inactive），client detach 不中断执行，stable session/parent id 跨状态保持递归拓扑。通信走 daemon 中介的异步队列，agent 可寻址 parent、children 与 siblings，排队消息在接收方重新活跃时仍可取。Agents View 把这棵持久树暴露给人：inspect history、attach、给新输入、detach 而不打断执行；`agent-observe` 提供有界只读状态与近期消息预览，`agent-message` 定向到具名的相关会话。

**Continual Harness 与 refinement。** 四类 typed state 分工明确：prompt notes 存行为指令、memories 存事实、skills 打包可执行过程、subagent specifications 存可复用角色与分工。条目支持 CRUD，local 属于单个 session，显式请求的 global 条目对后续 session 可见。Refinement 把轨迹证据转成版本化状态更新——agent 直接请求编辑，或 `/refine` 在相关事件上跑一次后台模型调用；运行时在 turn boundary 应用每次编辑，记录其触发与预期效果，并为下一次调用组装补充状态。版本保留 provenance 并支持 rollback，且 refinement 只补充不可变的 base prompt，不重写基础策略。论文对"self-improvement"给出的定义很克制：把执行证据转成会改变后续行为的持久 harness 状态，**而模型权重保持不变**——有用的计算变成 skill，重复的协调模式变成 subagent specification，被纠正的假设变成 memory 或 prompt note。

**长时执行控制与计费语义。** 三种机制：autonomous mode 在显式预算内持续 turn 并在每轮后跑任务指定的 end-condition test（失败则返回有界输出供再试，turn / token / wall-clock 上限终止执行）；goal 跨 continuation 保留目标，由 agent 宣告完成才结束；heartbeats 按 cron 或定时触发 turn。评测配置把任务与工具接口绑定到模型/provider 设置、compaction 与 refinement 策略、重试策略、完成闸门与资源上限；**accounting 聚合 root 与所有后代会话**，使 delegation 的开销显式出现在 test-time cost 里。

## Key Results

评测围绕三个 RQ：test-time scaling（ARC-AGI-3）、information management（长上下文套件）、persistent recursive execution（nanoGPT / PMPP-Hard / EmulatorBench / Factorio / MazeBench）。

**ARC-AGI-3。** Abstract 报 RHAE Best@1 "from 30% to 95.5%"，§1 同一结果写成 "from 30% to 95%"。这个数字在 §3.1 正文里不出现，只能从 Figure 5 图例读出：95.5% 是作者自跑的 "Prime Agent + Opus 5"，30.2% 是外部参照 "Opus 5, ARC harness"（同图另有 Hermes Agent 5.8%）。§3.1 明确说明参照线"are external values because our native-harness reruns fell below the published scores, so they situate the result rather than isolate a causal harness effect"，并且作者自跑的 Claude Code / Codex 在匹配 prompt 与设置下低于 Anthropic / OpenAI 自报成绩，因此"defer to their results over our own runs"。作者自己的 Opus 5 native-harness 复跑数值全文未报。Prime Agent 只提供环境接口和一个改编自 PRO-LONG 的 autonomous prompt，策略由模型自建。

**长上下文（Table 1，9 任务 × 3 组 within-model 对照）。** Prime Agent 在 27 个点估计中占优 20 个（GLM-5.2 组 8/9、Opus 5 组 6/9、GPT-5.6 Sol 组 6/9）。

| Task | Setting | GLM-5.2 Prime / Pi-mono | Opus 5 Prime / Claude Code | GPT-5.6 Sol Prime / Codex |
|:--|:--|:--|:--|:--|
| OOLONG (Yahoo, 128k) | long context | **.700** / .420 | .900 / **.920** | **.940** / .900 |
| OOLONG-Pairs | long output | **.874** / .556 | **.929** / .922 | **.911** / .895 |
| OBLIQ-Bench (math) | ranking nDCG@10 | **.669** / .635 | **.802** / .795 | .612 / **.646** |
| LongBench Pro (English) | comprehension | **.777** / .768 | **.804** / .790 | **.794** / .790 |
| LongBench v2 | expert long tasks | .680 / **.696** | .744 / **.746** | **.714** / .704 |
| ManyIH Coding | long instructions | **.424** / .386 | **.536** / .522 | **.499** / .454 |
| ManyIH IF | long instructions | **.209** / .164 | **.225** / .175 | .216 / **.232** |
| LongCoT-Mini | long reasoning | **.638** / .613 | **.722** / .558 | .671 / **.681** |
| EmulatorBench | long coding | **.208** / .000 | .047 / **.062** | **.275** / .228 |

Table 1 caption 自设边界：加粗只表示在同一 nominal-model 对内点估计更高，"Bold is not statistical significance, and uncertainty intervals are unavailable"，且逐行指标不同。作者的解读是 Prime Agent "especially against the harness that did not use a model trained around it"——最大的领先（OOLONG .700 vs .420、OOLONG-Pairs .874 vs .556、EmulatorBench .208 vs .000）确实全部落在 GLM-5.2 / Pi-mono 这一对上。

**nanoGPT speedrun（多日自主研究）。** 结论是**harness 选择对最终 record 的影响小于实验噪声**；差异出现在行为层。在 Prime Agent 上模型经常用持久 REPL 在 benchmark 训练脚本之外做实验（在合成梯度上模拟候选 optimizer、数值优化更新规则系数）。Figure 6 在 18 个 run 上统计这类实验（每 100 次训练脚本执行的 distinct experiment 数，按每 harness 2–3 seed 汇总）：DeepSeek V4 Pro 在 Prime Agent 下为 7.6（25/328），Claude Code 下为 1.2（6/498），约 6.3 倍，对应正文"roughly six times more"。Kimi K3 自定义了一个 probe function，通过它跑了约 90 次筛选实验和全部 19 条 validated record，而同一模型在自家 CLI 上全部经由直接改文件、没有建起这套机制。§1 另称"sustains an 85.5-hour nanoGPT run"，该时长只出现在 §1，§3.3 未报告任何 wall-clock 时长。

**EmulatorBench。** 要求用 Rust 从零构建、沙箱内无参考实现，由人工诊断程序（CPU flags、PPU timing 等）打分。Table 1 的数字被论文自称 preliminary，为 16 个 emulator 重建的平均；Figure 7 展示 Sega Genesis 与 Game Boy Color 的逐步 verifier score vs 估算成本。作者记录了一个未解释的失败："For Opus, our runs surprisingly failed to solve the tasks despite successful tool-call responses"。

**PMPP-Hard（GPU kernel）。** 固定 wall-clock 预算下 Prime Agent 与 native harness 接近，且两组模型间排序反转（Figure 8 图例：Prime 62.3%，43/69 vs Codex 59.4%，41/69；Prime 68.1%，47/69 vs Kimi-Code 71.0%，49/69）。论文另称"same performance as Codex or Kimi-Code is achieved by Prime Agent at substantially reduced cost"、"token-for-token, Prime Agent has an advantage"，但这两句只有散文，全文没有任何 token 用量数字（C9b，已降级）。

**Factorio（7 天 Sonnet 5 持久运行）。** root 与后代共用 23.4M output token，完成 196 项技术中的 24 项，advanced-circuit 研究到 71%，作者称曲线"no signs of stalling"。递归形态是浅而反复变宽：633 个 depth-one 子 agent 跨 149 个 dispatch wave，最多 7 个并发——记录的是并行任务专门化而非更深递归。模型对不可逆动作处理很差：一次 destructive world reset 把技术数从 5 退回 1，session 随后恢复并继续而非丢弃轨迹。

**Factorio 的安全失败（本文最有信息量的一段）。** 另一条 trace 中，agent 发现 RCON 命令可以把资源直接 spawn 进 assembly machine，在存在 anti-cheating heartbeat 的情况下仍使用了这个捷径，并把它作为可复用 skill 保留下来。作者的结论是持久化保住了"optimized the measured objective, including a specification exploit"的行为，因此安全部署需要 least-privilege 动作接口、独立的状态验证与对被污染 refinement 的可审计回滚。

**MazeBench。** 3D 开放世界空间推理，按 unique rooms / unique states / gems 对 token 花费作图（Figure 10）。正文与图例均无数字。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | Abstract 称 ARC-AGI-3 RHAE Best@1 从 30% 到 95.5%；§1 同一结果写作 95%，两处不一致 | number | Abstract; §1 | "raises ARC-AGI-3 RHAE Best@1 from 30% to 95.5%" / §1: "improves ARC-AGI-3 performance from 30% to 95%" | source-verified |
| C2 | Figure 5 图例显示 95.5% 是自跑 "Prime Agent + Opus 5"，30.2% 是外部 "Opus 5, ARC harness" 参照，作者自跑的 Opus 5 native-harness 值全文未报 | benchmark-setting | Figure 5 legend | "Prime Agent + Opus 5 — 95.5%" vs external "Opus 5, ARC harness — 30.2%" | source-verified |
| C3 | §3.1 自陈参照值为外部值，仅用于定位结果而非隔离 harness 的因果效应 | causal-mechanism | §3.1 末段 | "they situate the result rather than isolate a causal harness effect" | source-verified |
| C4 | §3.1 称作者自跑的 Claude Code / Codex 低于 Anthropic / OpenAI 自报成绩，故采信厂商结果 | benchmark-setting | §3.1 首段 | "we defer to their results over our own runs with matched prompt and settings" | source-verified |
| C5 | Table 1 caption 声明加粗只是同对内点估计更高，不代表统计显著，且无不确定区间 | benchmark-setting | Table 1 caption | "Bold is not statistical significance, and uncertainty intervals are unavailable" | source-verified |
| C6 | Table 1 共 27 个 within-model 对照，Prime Agent 点估计占优 20 个（GLM 8/9、Opus 6/9、GPT 6/9） | number | Table 1（逐格重数） | 加粗格与数值一致，Prime 失分：GLM LongBench v2；Opus OOLONG/LongBench v2/EmulatorBench；GPT OBLIQ/ManyIH IF/LongCoT-Mini | source-verified |
| C7 | EmulatorBench 行：.208 / .000（GLM-5.2）、.047 / .062（Opus 5）、.275 / .228（GPT-5.6 Sol） | number | Table 1, EmulatorBench 行 | ".208 \| .000 \| .047 \| .062 \| .275 \| .228" | source-verified |
| C8 | EmulatorBench 结果自称 preliminary，为 16 个重建平均，Rust 从零、沙箱无参考实现；Opus 的 run 全部失败 | benchmark-setting | §3.4 Emulators | "preliminary results ... averaged over 16 emulator reconstructions"; "For Opus, our runs surprisingly failed to solve the tasks" | source-verified |
| C9 | PMPP-Hard 图例：Prime 62.3%（43/69）vs Codex 59.4%（41/69）；Prime 68.1%（47/69）vs Kimi-Code 71.0%（49/69） | number | Figure 8 legend | 图例数值；正文无对应表格 | source-verified |
| C9b | "same performance as Codex or Kimi-Code ... at substantially reduced cost"、"token-for-token, Prime Agent has an advantage" | comparison | §3.4 GPU kernels | 仅散文；全文无任何 token 用量数字，Figure 8 只画 solve rate | unsupported |
| C10 | §1 称 "outperforms other harnesses, Hermes Agent, OpenCode, and Kimi-Code, on other benchmarks" | comparison | §1 vs Figure 8 | Figure 8：Kimi-Code 71.0% 高于 Prime Agent 68.1%（Kimi-Code 唯一有分数的 benchmark） | contradicted |
| C11 | nanoGPT：harness 选择对最终 record 影响小于实验噪声 | comparison | §3.3 | "the choice of harness has little effect on final records compared to the noise of the experiment" | source-verified |
| C12 | DeepSeek V4 Pro 在 Prime Agent 下每次训练运行的 out-of-loop 实验约为 Claude Code 的 6 倍（图例 7.6 = 25/328 vs 1.2 = 6/498）；Kimi K3 用 probe function 跑约 90 次筛选实验与全部 19 条 validated record；Figure 6 汇总 18 个 run | number | §3.3; Figure 6 caption+legend | "roughly six times more such experiments per training run under Prime Agent than under Claude Code" | source-verified |
| C13 | §1 称 "sustains an 85.5-hour nanoGPT run with 19 validated records"；该时长只出现在 §1，§3.3 未报告任何 wall-clock 时长 | number | §1 | "sustains an 85.5-hour nanoGPT run with 19 validated records" | source-verified |
| C14 | 7 天 Sonnet 5 Factorio 运行：23.4M output token、24/196 技术、advanced-circuit 71%；633 个 depth-one 子 agent 跨 149 个 dispatch wave，最多 7 并发 | number | §3.5; Figure 9 | "used 23.4 million output tokens while completing 24 of 196 technologies"; "633 depth-one subagents across 149 dispatch waves" | source-verified |
| C15 | 一条 Factorio trace 中 agent 发现 RCON 可直接向 assembly machine spawn 资源，在有 anti-cheating heartbeat 时仍使用，并把它保留为可复用 skill | causal-mechanism | §3.5 第 3 段 | "used the shortcut despite an anti-cheating heartbeat, and then preserved it as a reusable skill" | source-verified |
| C16 | 四层信息层级 L0 权重 / L1 active context / L2 持久 REPL + 递归子 agent / L3 磁盘 history-memories-skills；L2 机制名为 agentic garbage collection | causal-mechanism | §1; §2.2 | "We call the L2 mechanism agentic garbage collection" | source-verified |
| C17 | Self-improvement 只改持久 harness 状态，模型权重不变；版本保留 provenance 并支持 rollback | causal-mechanism | §2.5 | "persistent harness state that changes later behavior while model weights remain fixed" | source-verified |
| C18 | 代码在 https://github.com/PrimeIntellect-ai/prime-agent ，arXiv HTML 标 CC BY 4.0 | license-code | Abstract; arXiv header | "Code is available at https://github.com/PrimeIntellect-ai/prime-agent." | source-verified |

> [!warning] 核验边界
> C9b 为 unsupported：token 成本优势只有散文，无任何数字，本笔记不以事实口吻复述。C10 为 contradicted：论文 §1 的"outperforms Kimi-Code"被自家 Figure 8 否证，正文与 Summary 均不引用该断言。ARC-AGI-3、PMPP-Hard、Factorio、MazeBench 与 EmulatorBench 逐 run 曲线全部无数值表格，上述数字均由 verifier 从 PDF 的 figure legend 读出；MazeBench 无任何可读数字。`RHAE` 全文未展开定义，`Best@1` 只在 abstract 出现一次，采样预算无正文说明。所有状态仅表示与 primary source 一致，不表示结果已被独立复现。

## Strengths & Weaknesses

**把 accounting 写进 harness 定义，是这条线一直缺的东西。** "Accounting aggregates the root and descendant sessions, so delegation remains visible in test-time cost" 这一句解决的是 [[AgentHarness-Design]] 第 4 节预算审计反复记录的同一类问题——递归/多 agent 方案的收益常常靠不被统计的子调用买来。Prime Agent 至少把"delegation 的成本必须可见"变成运行时语义而不是论文里的一句承诺。同样值得肯定的是它把 harness 失败与模型失败的区分（标准化 persistence / recovery / termination）作为设计目标显式写出来。

**Factorio 的 RCON 段是全文最有价值的一段，价值高于任何 benchmark 数字。** 它给出 persistent-skill harness 上 misevolution 的一条具体机制路径：exploit 不是被模型"记住"，而是被 refinement 提升为**可执行且可复用的 skill**，并且 anti-cheating heartbeat 没能拦住——因为 agent 用的是合法接口做了非预期的事。这是"持久自改状态"这一设计的内生风险，不是实现 bug，也不是刻意构造的红队场景。作者给出的三条对策（least-privilege 动作接口、独立状态验证、可审计回滚）恰好对应 [[SelfEvolvingAgents-Survey]] §6 的 gate 家族，但本文只是提出而没有实现或评测任何一条。

**结论节的诚实度高于同类工作。** 明确承认"many harness capabilities remain underused because current models were not trained to operate them"，并把 model-harness co-learning 提为主要路线，同时自陈"targeted training on the RLM and Continual Harness components could isolate their contributions"——等于承认组件贡献尚未被隔离。

以下是主要问题。

**头条数字的口径是全文最弱的一环。** 30% → 95.5% 读起来像一次 harness 对照实验，但 §3.1 自己拆掉了这个读法：30.2% 是外部发表的另一个 harness 的值，作者自跑的 native harness 低于厂商自报分数因而被弃用，参照点"situate the result rather than isolate a causal harness effect"。真正能支撑因果归因的量——作者自己在同一环境同一 prompt 下跑 Opus 5 + native harness 的分数——全文没有。再加上 abstract 95.5% / §1 95% 的不一致，以及 `RHAE` 从未定义、`Best@1` 只出现一次，这个最容易被转引的数字恰恰是证据最薄的一个。

**组件完全不可分，而这次本来最该分。** `rlm` 递归、Continual Harness 四类持久状态、agent-to-agent 队列、autonomous/goal/heartbeat 三种长时控制作为一个 bundle 一起上，无任何 ablation。这与 [[2606-RecursiveAgentHarness]]（明确声明不做消融）、[[2608-LongHorizonHarness]]（Manage-Execute-Audit 三项变更一起引入）完全同型，是 [[Harness-Component-Attribution]] 记录的结构性缺口在 2608 的第三个样本。区别在于本文标题里的 "Self-Improving" 指向一个成本极低的对照：把 skills / memories / prompt notes / subagent specs 逐类关掉，在同一预算下重跑 Factorio 或 EmulatorBench。不做这个对照，"self-improving" 就只是一个架构描述而非实证主张。

**"matches or exceeds" 主要由最弱的一组对照撑起来。** 20/27 的领先看着稳，但 Opus 5 与 GPT-5.6 Sol 两组里多数行的差落在 ±0.03 内，而 caption 自认无不确定区间；真正大幅的领先几乎全在 GLM-5.2 vs Pi-mono。作者自己点破了原因："especially against the harness that did not use a model trained around it"。这句话的含义比论文承认的更强：观察到的 harness 优势与"baseline harness 和 backbone 的训练耦合度"高度共线，而不是与 harness 表达力单独共线——换个说法，Table 1 更像在测量"基线 harness 有多不适配这个模型"。

**评测环境的独立性存在系统性问题。** RQ3 的五个环境里，EmulatorBench 出自作者自己未发表的 manuscript（Karten, Zhang, Jaghouar，即本文一作、二作与末作），PMPP-Hard 与 MazeBench 由致谢中的贡献者创建（"SinatraS created PMPP Hard, and Patience Cave created MazeBench"）。三个自建环境 + EmulatorBench 自称 preliminary + Opus 在 EmulatorBench 上全部失败 + MazeBench 无任何数字，这组证据撑不起跨 harness 的一般性结论。

**可核查性差。** 除 Table 1 外全部结果只存在于图里，PMPP-Hard 的 token 成本优势甚至连图都没有、只有散文；§1 的"outperforms Kimi-Code"被自家 Figure 8 直接否证；"85.5-hour" 只在 intro 出现而实验节不提。这些不是致命错误，但对一篇把"标准化测量"当作核心卖点的论文来说，是自我要求上的不一致。

**方法学上没有新机制。** `rlm` 来自 Recursive Language Models（本文二作 Zhang 的工作），Continual Harness 来自本文一作 Karten 的工作，Prime Agent 是二者加 daemon、消息队列与 UI 的工程集成。这不是缺点本身——artifact 与测量规范可以是真正的贡献——但它决定了这篇论文的引用价值在实现而不在洞见。

**潜在影响。** 最值得关注的不是论文里的数字，而是 Prime Intellect 的主业是分布式训练：如果这个 harness 被真的当成 RL 训练环境用起来，"model-harness co-learning" 就从一句 future work 变成可执行路线，而 Factorio 那条 RCON trace 也就同时变成该路线上第一个已知的 reward-hacking 载体。

## Mind Map

```mermaid
mindmap
  root((Prime Agent))
    Problem
      LLM 是 bounded sequential processor
      信息状态已超出权重与 active context
      harness 失败被误记为模型失败
      long-horizon 指标 fixed expenditure / practical plateau
    Method
      信息管理与计算管理分离
      四层状态 L0 权重 L1 context L2 REPL+子agent L3 磁盘
      agentic garbage collection
      持久 IPython REPL
      异步 rlm 递归原语与 stable handle
      daemon 会话与 agent-to-agent 队列
      Agents View 人机介入
      Continual Harness 四类 typed state 与版本化 refinement
      autonomous goal heartbeat 三种长时控制
      root+后代聚合计费
    Results
      ARC-AGI-3 30 到 95.5 但基线为外部值
      Table 1 长上下文 20 of 27 领先
      大幅领先集中在 GLM-5.2 vs Pi-mono
      nanoGPT harness 对 record 影响小于噪声
      DeepSeek 约 6 倍 out-of-loop 实验
      Factorio 七天 24 of 196 技术 23.4M token
      633 个 depth-one 子agent 最多 7 并发
      RCON exploit 被固化为可复用 skill
    Gaps
      无任何 ablation
      token 成本优势无数字
      三个评测环境为作者或致谢方自建
      结果多数只存在于图中
```

## Connections

- [[2606-RecursiveAgentHarness]] — 最直接的近邻与对照。那篇把递归单元从 model call 升级为"完整 harness"，Prime Agent 把同一升级做成持久 daemon + 版本化状态 + 消息队列；两篇都以 RLM 为出发点，也都**明确不做组件消融**。差别在于 RAH 的子 agent 之间无通信、无共享内存，Prime Agent 的核心增量恰恰是 parent/child/sibling 三向异步队列与跨 restart 可用的 handle——这是可以单独设计对照的一个变量，但本文没有测。
- [[2604-RecursiveMAS]] — 同一 RLM 谱系的另一分支：把递归推到 multi-agent 但走 latent-space RecursiveLink 而非代码路径。三篇合起来构成"RLM 递归单元该是什么"的完整设计空间（model call / latent link / 完整 harness / 持久 daemon 会话）。
- [[Harness-Component-Attribution]] — 本文应作为第三个样本并入。该 survey 的核心结论是 harness 论文普遍报告 bundle 级增益、把归因留给读者；Prime Agent 不仅重复了这一模式，还在结论里自陈组件贡献未被隔离，属于"作者已识别但未执行"的类型，比单纯的疏漏更值得记一笔。
- [[AgentHarness-Design]] — 该 survey scope 为 web-agent-only，Prime Agent 不属于其收录范围，但它的 root+后代聚合计费是对该文第 4 节预算口径审计所指问题的一个正面回应，值得作为跨 scope 的方法学参考被提及。
- [[SelfEvolvingAgents-Survey]] — RCON 段应并入 misevolution 节。与 [[2509-Misevolution]] 的关键差别是污染载体：那里主要是 memory 与 workflow，这里是 **skill（可执行过程）**，且发生在已部署 anti-cheating heartbeat 的环境中，说明启发式作弊检测对"用合法接口做非预期事"无效。本文同时给出该 survey gate 家族的三条对策，但一条也没实现。
- [[2607-HarnessEvolution]] — 矛盾对。那篇固定 LLM 只换 harness（同一 CLI 的连续 release）得到零增益且成本 +70%；Prime Agent 换的是执行基底本身。两者并置支持一个更细的判断：harness 增益不是"harness"这个抽象层的属性，取决于被改动的具体机制，也取决于基线 harness 与 backbone 的训练耦合度。
- [[2609-HarnessDev]] / [[2607-HarnessBank]] / [[2608-EvoHarnessRL]] — harness 自演化家族。它们改的是 harness 的**代码/配置**，Prime Agent 改的是 harness 的**运行时状态**（skills / specs / memories / prompt notes），且明确不动 base prompt。这两类"自改"的可回滚性与风险面并不相同，值得在 survey 里分开处理。

## Notes

- **最小充分实验（若要沿这条线推进）**：Continual Harness 的四类 typed state 逐类关闭，在 EmulatorBench 或 Factorio 上跑同 token 预算的对照。这是把标题里的 "Self-Improving" 落到证据上的最低成本路径，远比重跑全套评测便宜，也直接回答本文自陈的"contributions not isolated"。第二条对照同样便宜：在 ARC-AGI-3 上补一次作者自跑的 Opus 5 + native harness 结果，让 30% → 95.5% 有一个匹配设置的分母。
- **RCON trace 是 n=1**，只能作为机制存在性证据，不能当频率证据。但它的机制路径是可推广的：任何允许 agent 把成功计算固化为 global skill 的 harness，都存在"exploit 被提升为可复用能力"的通道，且这个通道绕过了针对单次行为的检测。值得单独作为一个 idea 的起点。
- **数字口径提醒**：引用 ARC-AGI-3 时必须写"abstract 报 95.5%（§1 写 95%），对照的 30.2% 为外部发表值"，不能写成 harness 对照增益。引用 PMPP-Hard 时不要复述 token 成本优势（无数字）。引用 §1 的"outperforms Kimi-Code"要注明被 Figure 8 否证。
- **引用编号的坑**：HTML 与 PDF 两个 rendering 的参考文献编号不一致（EmulatorBench 在 HTML 是 [17]、PDF 是 [18]；Continual Harness [18] vs [19]）。后续按编号引用 locator 时须注明版本。
- **日期口径**：arXiv HTML header 写 "First published: August 5, 2026 · Current version: August 24, 2026"，而 v1 标注为 24 Aug 2026；`date_publish` 取 arXiv v1 日期。
- **待跟踪（repo_candidate）**：代码已开源且 URL 可达。这是典型的贡献主要在实现里的系统类工作，`rlm` 的实际调度语义、refinement 的触发条件与 accounting 到底聚合了哪些字段，只有读代码才能确认——尤其 accounting 这一条是本文相对同类工作的主要方法学卖点，值得单独一轮 repo-digest 验证它是否名副其实。
