---
title: "Agentic Compilation: Mitigating the LLM Rerun Crisis for Minimized-Inference-Cost Web Automation"
authors:
  - "Jagadeesh Chundru"
institute:
  - "Selfotix"
date_publish: "2026-04-08"
venue: "arXiv"
tags: ["gui-agent", "web-agent", "task-planning"]
url: "https://arxiv.org/abs/2604.09718"
arxiv_id: "2604.09718"
doi: "10.48550/arXiv.2604.09718"
cite_key: chundru2026agentic
code:
rating: "2"
content_scope: "full-text"
verification_status: "unverified"
date_added: "2026-08-10"
---
## Summary

把 web automation 的 LLM 用法从 per-step 连续推理改成"编译一次、确定性重放"：单次 LLM 调用读入 DOM Sanitization Module 压缩后的语义骨架与用户意图，产出 JSON workflow blueprint，随后由轻量 runtime 零推理执行，作者据此把推理成本从 O(M×N) 降为对 M 的 amortized O(1)。三个自定义企业任务上 zero-shot 编译成功率 80–94%，单次编译实测 $0.002–$0.092。但作为核心卖点的 "$150 → <$0.10" 对比里，$150 一侧是纯假设推出来的估计值——全文没有跑过任何 continuous agent baseline，也没有任何 blueprint 失效率或 recompilation 频率的测量。

## Problem & Motivation

作者给 continuous-loop web agent（ReAct / CoT 式，每步调一次模型看 browser state 再出 action）的成本结构起了个名字：**Rerun Crisis**——当一个逻辑结构不变的 workflow 被重复执行 M 次，agent 每次都要重新推导一遍已知的动作序列，把本该是常数成本的 planning 问题变成随执行频率线性增长的推理支出。

论文的定位很明确：这不是 agent 智能问题，也不是任务难度问题，而是"把概率推理反复施加在确定性的、已解决的问题上"的结构性浪费（Sec 1.1）。作者主张业界把它误读为"API 降价就能解决的 pricing issue"，实则是架构缺陷（Sec 1.2）。

值得注意的是，论文对这个动机的经验支撑很薄：Sec 1.2 引用"社区 benchmark 显示开源 continuous agent 单任务推理成本 $1.00–$3.20"，但没有给出任何引用来源；"工程团队因账单耗尽而放弃 continuous-loop 框架"也只是 industry discourse 层面的转述。这篇的立场更接近 systems position paper 而非实证研究。

## Method

三段式 pipeline：**DOM sanitization → one-shot LLM compilation → supervised deterministic execution**，中间插一道 HITL verification gate。作者显式对齐编译器理论：自然语言意图 = source code，LLM = compiler，JSON blueprint = bytecode/IR，execution engine = runtime。

**DOM Sanitization Module (DSM)**（Sec 3.1）——单次 DOM traversal 做三件事：

1. *Noise Eradication*：无条件剪掉 `<script>`、`<style>`、`<svg>`、base64 payload 等非内容子树。
2. *Signal Extraction*：移除 `display:none` / `visibility:hidden` 节点，避免 LLM 幻觉出对不可交互元素的操作。
3. *Attribute Cleansing*：激进剥离易变的 utility CSS class，保留语义标识符（BEM class、`data-*`、ARIA role）。

第 3 条是全篇最关键的设计赌注：作者要靠"把 selector 锚定在应用的永久语义结构上"来对抗 UI redesign 和 A/B test。作者声称三步合计压缩 token payload **up to 85%**，但全文没有给出这个压缩率的任何测量数据。

**One-Shot Compilation**（Sec 3.2）——sanitized HTML skeleton + 页面 URL + 用户意图一次性送入模型，system prompt 强制输出完整可执行的 JSON workflow schema，不允许模型延迟决策或反问。prompt 里编码一条 **Semantic Selector Priority Hierarchy**：必须优先选 ARIA role / `data-*` / 稳定 class，而非 `nth-child` 这类脆弱的位置路径。同一次调用内模型还要识别 pagination 模式、构造循环、产出 extraction mapping。

**执行**（Sec 3.3）——blueprint 先给人类操作员审阅（可 accept / reject / 手工修改），主要是防不可逆副作用（表单提交、账户变更）。批准后，轻量 execution engine 遍历 JSON 并发出 native browser API 调用，编译后与模型的连接完全断开。为适配 SPA 的异步渲染，engine 用 **dynamic wait heuristics**（监听 DOM mutation 事件与 network-idle 信号）替代固定 sleep timer。失败时 HITL 边界兼作确定性人工兜底：直接注入修正后的 selector，或用局部交互录制器桥接失败点，无需重启整个流程。

需要指出：**论文从头到尾没有给出 JSON blueprint 的 schema 定义、示例或语法**，也没有放出代码。作为一篇把 IR 当作核心贡献的系统论文，这是相当大的缺口。

**Lazy Replanning Architecture**（Sec 3.4）——三种失败触发重规划：(a) *UI Changes*，结构变更导致语义 selector 解析为 null；(b) *Execution Breaks*，网络延迟 / SPA 渲染超时 / 意外弹窗打断序列；(c) *Plan Fails*，blueprint 执行成功但抽取结果违反 schema 约束。engine 捕获变异后的 DOM 状态回送给 compiler 做 targeted selector healing。作者强调这不等于退回 continuous agent：control flow 始终封闭在确定性 runtime 内，LLM 只作为 exception handler 解一个 null pointer，不改变已编译的操作序列，因此推理成本是结构性 UI 波动的函数 O(R) 而非执行循环 O(M×N)。

**但 Sec 5.5 把"automated recompilation"列为 future work，而 Sec 3.4 / 5.2 / 5.4 用现在时描述该机制正在运行**（"the execution engine halts and **triggers** the lazy replanning compiler"、"The engine **captures** the mutated DOM state and **routes it back** to the LLM compiler"、"this predictable halting **is utilized** as the precise trigger for the hybrid fallback and selector healing mechanisms"）。论文内部对"自动 healing 是否已实现"自相矛盾；无代码可核，也无论哪种解读都完全没有实验。

## Key Results

**成本模型（Sec 4.1）**

- 连续式：`Cost_cont = M × Σ_{i=1..N} [S_i × C_t]`，随 M 线性增长，标为 O(M×N)
- 编译式：`Cost_oneshot = 1 × (S_compile × C_t) + C_exec`，C_exec（算力与浏览器 API 调用）被断言相对 frontier API 费用可忽略，故对 M 而言 amortized O(1)

**成本对比（Sec 4.2，代表性企业抽取任务：500 个 profile × 每个 5 个字段，假设每页原始 DOM 20,000 token）**

| 方案 | 推理成本 | 性质 |
|:--|:--|:--|
| Unoptimized continuous baseline（~2,500 次 API 调用） | **estimated** $150.00 | 假设推算，未实测 |
| Optimized continuous baseline（90% caching / DOM-diffing） | **estimated** $15.00 | 假设推算，未实测 |
| One-shot compilation | $0.002–$0.10 | 实测（Table 1） |

作者据此宣称最高 **1500× 成本削减**。

**这里必须说清楚证据强度的不对称：$150 与 $15 是 estimate，$0.002–$0.092 是 measurement。** 论文从未给出所假设的 per-token 价格 `C_t`，从未指明 baseline 用的是哪个模型，也从未真正运行过任何一个 continuous agent。按其自述参数反推（2,500 次调用 × 20,000 token = 50M input token，$150 / 50M ≈ **$3.00 / 1M token**）——这个隐含单价大致对得上 Sonnet 级输入定价，属合理量级，但它是笔者的推算而非论文给出的。$15.00 更直接：就是 $150 × 0.1。因此"1500×"这个 headline 是「一个假设值 ÷ 一个实测值」。

**Table 1：五个 frontier model 的单次编译实测（OpenRouter，sanitized skeleton ≈10,000–12,000 token）**

| Model | Input → Output tokens | Cost (USD) | Speed (TPS) | Result |
|:--|:--|:--|:--|:--|
| Claude Opus 4.6 | 11,628 → 1,340 | $0.0916 | 96.9 | Success |
| Claude Sonnet 4.5 | 11,628 → 1,670 | $0.0599 | 98.6 | Success |
| GPT-5.2-Codex | 9,951 → 1,447 | $0.0377 | 115.7 | Success |
| Qwen3.5 397B | 10,738 → 3,000 | $0.0172 | 56.2 | Success |
| Qwen3 Coder Next | 10,536 → 550 | $0.0020 | 131.6 | Success |

五个模型都产出了语法合法、可执行的 JSON blueprint。Gemini 2.5 Flash 与 Claude 3.5 Haiku 在预实验中因 schema-constrained generation 失败率过高被排除（作者强调是系统性编译失败，不是单纯因为便宜）。

**Table 2：三个内部企业任务的执行评测**

| Task Modality | Compilation Attempts | Successful Blueprints | Execution Accuracy |
|:--|:--|:--|:--|
| T1: High-Volume Paginated Extraction | 50 | 46 (92%) | 98.0% |
| T2: Form Filling | 10 | 8 (80%) | 95.0% |
| T3: Technology Stack Detection | 50 | 47 (94%) | 96.0% |

- **T1**：每页 30 条商户 profile × 10 个分页状态，每条抽 5 个字段（name / URL / address / website / phone）；执行时加 0.1s 随机步间延迟与 7s 翻页延迟以规避限流。
- **T2**：把结构化语义 payload 映射到混淆过的表单字段（含非标准 input 类型与下拉菜单）；需要 webhook 动态解析 payload 的配置在 1 分钟内完成。
- **T3**：访问目标域名、分析 sanitized DOM skeleton 识别 CMS / analytics tracker / 前端框架，不依赖 pattern matching 启发式。

编译失败（6%–20%）被归为三类：Schema Violations（输出非法 JSON）、Semantic Misalignments（选中视觉显著但不可操作的 DOM 节点）、Reasoning Depth Exhaustion（T2 中多步条件依赖映射失败）。作者论证失败被底层 LLM 的空间推理上限所界定，而非执行引擎的缺陷；并强调编译失败 ≠ 系统失败，因为 declarative JSON 可读可局部修补，HITL 操作员数秒内改一个 selector 即可，从而在保持 amortized O(1) 的前提下把可靠性抬到 near-100%。

**评测范围（Sec 5.1）**：**没有使用任何标准 web agent benchmark**。作者显式拒绝 WebArena / Mind2Web，理由是这些 macro-benchmark 测的是多样新环境下的泛化零样本推理，而本架构针对的是重复性结构化 workflow 的经济性扩展；直接对打会把底层 LLM 的空间推理局限与架构的成本扩展性质混为一谈。评测因此落在专有企业 DOM 上，作者承认这"限制了独立复现"，并称之为刻意的方法论选择。Sec 5.5 又把"对既有 web agent benchmark 做正式评测"列为 future work。

## Evidence Ledger

> 状态来自一次独立 verifier pass（只给 primary source、claim package 与状态定义，不给本笔记的分析与优缺点判断）。`source-verified` 仅表示原文确实包含该信息，不表示结果已被独立复现。

> 本轮为 `--prepare-only`，Finder 未自判 source-verified；全部 claim 状态为 `pending`，等待独立 verifier 裁定。excerpt 均取自 arXiv:2604.09718v2 HTML 全文。

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | 论文称 5-step workflow 跑 500 iterations 的 continuous agent 推理成本约 $150.00，激进缓存下仍约 $15.00 | number | Abstract; Sec 4.2 | "a continuous agent incurs approximately $150.00 in inference costs; even with aggressive caching, this remains near $15.00" | source-verified |
| C2 | $150.00 与 $15.00 均标为 "estimated"，建立在假设参数上（2,500 次 API 调用、每页 20,000 token 原始 DOM），论文未给出 per-token 价格 C_t，未指明 baseline 模型，也未运行任何 continuous agent | number / benchmark-setting | Sec 4.2 | "yields approximately 2,500 sequential API calls and an estimated total cost of $150.00" | source-verified |
| C3 | 单次编译成本为实测值，跨 5 个模型经 OpenRouter 记录，范围 $0.0020（Qwen3 Coder Next）至 $0.0916（Claude Opus 4.6） | number | Table 1 (Sec 4.2) | "Table 1: One-shot compilation performance across leading LLMs (OpenRouter)" | source-verified |
| C4 | "up to 1500×" 成本削减是 estimated $150 与 measured ~$0.10 之比，非两侧同口径实测 | number / comparison | Sec 4.2 | "a cost reduction of up to 1500× compared to un-optimized continuous agents under equivalent execution workloads" | source-verified |
| C5 | 成本形式化为 Cost_cont = M × Σ[S_i × C_t]（O(M×N)）与 Cost_oneshot = 1×(S_compile×C_t) + C_exec（amortized O(1)），其中 C_exec 被断言可忽略 | causal-mechanism | Sec 4.1, Eq. (2)(3) | "its monetary cost is negligible relative to frontier API fees" | source-verified |
| C6 | 论文自认 recompilation 的稀有性未被证明，O(R) 论证缺少纵向实证 | causal-mechanism | Sec 3.4 | "longitudinal empirical studies are required to mathematically prove the rarity of recompilation across the broader internet" | source-verified |
| C7 | DSM 宣称压缩 token payload "up to 85%"（Intro 与 §3.1 各出现一次，均为裸断言），全文无任何测量。Table 1 的 9,951–11,628 token 是评测页的 sanitized skeleton，与 §4.2 假设的 20,000 token 并非同一页；若强行对照仅得 41.9%–50.2% | number | Sec 3.1; Table 1 | "these operations compress token payloads by up to 85%" | source-verified（原表述"约 42%"为单端点取值，已按独立 verifier 复算改为区间） |
| C8 | 评测不使用标准 web agent benchmark；论文显式拒绝 WebArena / Mind2Web，改用专有企业 DOM 上的三个自定义任务 | benchmark-setting | Sec 5.1; Table 2 | "reliance on proprietary enterprise DOMs limits independent replication ... a deliberate methodological choice" | source-verified |
| C9 | Table 2：T1 46/50 (92%) / 98.0%；T2 8/10 (80%) / 95.0%；T3 47/50 (94%) / 96.0% | number | Table 2 (Sec 4.3) | "T1: High-Volume Extraction 50 46 (92%) 98.0%" | source-verified |
| C10 | 论文未运行任何 continuous-agent baseline（成本与成功率皆无），未报告 blueprint 失效率、时间衰减或 recompilation 频率的任何测量 | benchmark-setting | Sec 4–5 全篇（缺失证据） | Tables 1–2 只含 one-shot 结果；Sec 5.2 仅为论证性文字 | source-verified |
| C11 | §5.5 把 automated recompilation 列为 future work，而 §3.4 / §5.2 / §5.4 以现在时描述 selector healing 已在运行——论文内部对该机制是否已实现自相矛盾，无代码可核 | causal-mechanism | Sec 3.4; Sec 5.2; Sec 5.4 vs Sec 5.5 | "the execution engine halts and triggers the lazy replanning compiler" vs "First, automated recompilation … would partially recover the resilience advantages" | source-verified（原推断"已实现的是干净停机 + HITL"被独立 verifier 判为 unsupported，已改写为内部矛盾陈述） |
| C12 | near-100% 可靠性依赖人工修补失败的 blueprint，不是自主达成 | comparison | Abstract; Sec 4.3 | "HITL gate allows operators to manually patch isolated failures ... enabling near-100% execution reliability" | source-verified |
| C13 | "约 80% 的企业 workflow 具备稳定标准 HTML 结构"与"社区 benchmark 单任务 $1.00–$3.20"两项数字均无引用来源 | number | Sec 5.4; Sec 1.2 | "constrained to the approximately 80% of enterprise workflows characterized by stable, standard HTML structures" | source-verified |
| C14 | 论文未提供代码链接，正文未给出 JSON blueprint 的 schema、语法或示例 | license-code | 全文（缺失） | 无 code/artifact 声明；Figure 2 仅以方框标注 "JSON Blueprint" | source-verified |
| C15 | §4.2 把 Table 1 实测上限 $0.0916 上取整成 $0.10（1500× 由此得出），Abstract 与 §6 则写 $0.092——同一数字两种取整，1500× 依赖较宽松的那一版 | number | Sec 4.2 vs Abstract/Sec 6 | "Total inference cost ranges from $0.002 to $0.10" vs "per-compilation costs between $0.002 and $0.092" | source-verified（原表述"内部不一致"过强，已按独立 verifier 意见改为取整口径差异） |

## Strengths & Weaknesses

**Strengths**

- **给一个真实的部署痛点起了准确的名字并写下了成本方程。** "Rerun Crisis" 这个 framing 有用：它把 web agent 的成本讨论从"模型多贵"拉到"架构决定成本随什么量增长"，Cost = M × Σ[S_i × C_t] 是可以被后续工作直接引用和批评的具体对象。对 harness 设计的 cost axis 而言，这个方程比论文任何一个数字都更有价值。
- **判据切得干净。** LLM 决定 control flow（continuous）vs LLM 只做 exception handler（compiled）——这条界线比"有没有缓存 / 有没有 memory"更能区分成本类别，也解释了为什么 AWM 类 workflow memory 仍困在 O(M×N)：它压的是 N，不是 M。
- **对适用边界的自述是诚实的。** Sec 5.3 明确承认 canvas / WebGL / viewport 驱动界面上 DSM 失效，multimodal continuous agent 更优；Conclusion 明说不主张全面取代 continuous agent。这种自限在 industry paper 里不常见。
- **失败模式分类可用。** Schema Violations / Semantic Misalignments / Reasoning Depth Exhaustion 三分，加上"编译失败被底层模型空间推理上限界定、而非执行引擎缺陷"这个归因，对做 harness 组件归因是可迁移的分析框架。

**Weaknesses**

- **核心成本 claim 是算术，不是测量。** 论文最重要的一个数字（$150）没有跑过任何实验：没有 baseline agent、没有指定模型、没有写下 per-token 价格。"1500×"是「假设值 ÷ 实测值」。方向上我认为结论大概率成立——去掉 M 次推理确实省钱——但**量级完全没有证据支撑**，任何引用这篇的工作都不应该搬运 1500× 或 $150。
- **成本对比把两个独立干预捆在一起。** baseline 假设 continuous agent 每步重发 20,000 token 的**原始** DOM，而编译路径用了 DSM 压缩后的骨架。这意味着节省里混了 (a) DOM sanitization 的上下文削减与 (b) 消除 per-step 推理两部分，论文从不拆分。公平的 ablation 应当给 continuous baseline 也配上 DSM——粗略推算这会让 baseline 立刻降约 45%，叠加 90% caching 后约 $8，headline 倍数随之从 1500× 掉到 ~80×。定性结论能活，量级不能。
- **最要命的缺口：适应性代价一个数都没有。** 编译式 workflow 是拿 adaptivity 换 cost，而论文**完全没有量化这笔交换**。没有 blueprint 失效率、没有随时间的成功率衰减曲线、没有 recompilation 频率、没有 selector healing 的成功率与成本、没有任何与 continuous agent 的成功率对照。Sec 5.2 "Cost-Resilience Trade-off" 整节是论证而非数据：结构性 UI 变更"每半年到一年一次"无引用，"recompilation 频率在运维上可忽略"是断言。作者自己在 Sec 3.4 承认这需要纵向研究来证明。**换言之，论文声称的 O(1) 实际是 O(S_compile × R)，而 R 从未被测量过。**如果目标站点的 R 随 M 增长（高频跑意味着更容易撞上部署窗口），O(1) 直接坍塌。
- **Sec 3.4 / 5.2 / 5.4 与 Sec 5.5 口径打架。** 前三处用现在时把 selector healing 写成正在运行的机制，后者把 automated recompilation 列为 future work。读者无法判断自动 healing 到底建没建；无论如何它没有被评测，也没有代码可核。
- **near-100% 是人机混合数字，不该与自主 agent 的成功率并列。** 它建立在人工修补失败 blueprint 之上。论文的 TCO 论证只记 API 美元，不记人工秒数与 HITL 审批环节的组织成本——而 HITL gate 是**每次编译**都必经的（Sec 3.3），不是仅在失败时触发。真实的 total cost 里有一项被系统性地记为零。
- **评测非公开、不可复现、规模小。** 三个自定义任务、专有 DOM、n=50/10/50。T2 的 80% 就是 8/10，一个样本抖动就是 10 个百分点，而这个 80% 正是 abstract 里 "80–94%" 区间的下界。"Execution Accuracy 98.0%" 的分母单位也没定义（按字段？按记录？按整次执行？）。
- **拒绝标准 benchmark 的理由半通半不通。** "别拿 Mind2Web 测成本架构、会混入模型推理能力的混杂因素"——这个 concern 是真的。但正确应对是**在标准环境里做受控对比**（同一模型、同一站点、compiled vs continuous 各跑一遍），而不是退到无人能复现的私有数据。尤其反讽的是，论文引用 Xue et al. 2025（Illusion of Progress，见 [[Papers/2504-OnlineMind2Web]]）来论证 continuous agent 的 benchmark 成绩不可信，随后自己交出了一份连独立核查都做不到的评测。
- **把 IR 当核心贡献却不公布 IR。** 没有 schema、没有示例、没有代码。这篇因此无法被复现，也无法被当作可依赖的工程参考——只能当作一个 framing 来引用。
- **单作者、公司 email（Selfotix）、主分类 cs.DC。**读的时候应按 industry position paper 而非同行评审实证研究来定权重。

**对领域的意义（个人判断）**：这篇的价值在命名和方程，不在数字。它把一个所有做 web agent 部署的人都遇到过、但很少被形式化的问题写成了可讨论的对象，并给出了一条清晰的架构分界线。但它同时是一个很好的反面教材：**当一篇论文的核心 claim 是成本削减时，"估算的 baseline vs 实测的 method"这种不对称会让整个数量级失去意义。**做 harness cost axis 的 survey 时，这篇应当被引为 framing 与 open problem 的来源，其 $150 / $15 / 1500× 一律不得作为经验数据转述。

## Mind Map

```mermaid
mindmap
  root((AgenticCompilation))
    Problem
      Rerun Crisis
        固定 workflow 重复 M 次
        每次重推已知动作序列
      成本随执行频率线性增长
        O(M×N) 结构性浪费
      动机证据薄弱
        1.00-3.20 美元社区数字无引用
    Method
      DSM 上下文压缩
        Noise Eradication
        Signal Extraction
        Attribute Cleansing 保留语义标识符
        宣称 up to 85% 但无测量
      One-Shot Compilation
        Semantic Selector Priority
        pagination 与 loop 一次推完
        输出 JSON blueprint 但未公布 schema
      HITL Verification Gate
        accept reject amend
        每次编译必经
      Deterministic Runtime
        native browser API 零推理
        dynamic wait 替代固定 sleep
      Lazy Replanning
        三种触发 UI变更 执行中断 计划失败
        LLM 仅作 exception handler
        自动化被列为 future work
    Results
      成本 estimated 150 vs measured 0.002-0.092
        1500× 为假设除实测
        未跑任何 continuous baseline
      Table1 五模型全部编译成功
      Table2 编译成功率 92 / 80 / 94
        执行准确率 98 / 95 / 96
        T2 仅 n=10
      near-100% 依赖人工修补
      无标准 benchmark
        显式拒绝 WebArena Mind2Web
        专有 DOM 不可复现
      适应性代价零测量
        无失效率 无衰减 无 R
```

## Notes

**这篇在 harness cost axis 上的定位**

它是目前少见的把 web agent 成本明确形式化为「架构决定 scaling 阶数」的工作。可用的是那条判据：*LLM 是否在运行时决定 control flow*。据此可以给 harness 分层——

| 层次 | 代表 | 对 M 的推理成本 |
|:--|:--|:--|
| Continuous loop | ReAct 式 | O(M×N) |
| Context reduction | [[Papers/2511-Prune4Web]]、DOM diffing | 降低 S_i，阶数不变 |
| Workflow memory | [[Papers/2409-AgentWorkflowMemory]] | 降低 N，阶数不变 |
| Compiled artifact | 本文、[[Papers/2504-SkillWeaver]] | 声称 O(1)，实为 O(R) |

**Connections**

- [[Papers/2504-SkillWeaver]] — 最直接的对照。同样是"把复用的交互模式蒸馏成可执行 program/API"，但 SkillWeaver 在 WebArena 与真实网站上做了带 baseline 的评测（相对提升 31.8% / 39.8%），还测了 skill 跨 agent 迁移。两篇的架构直觉几乎一致，证据强度差一个量级。本文没有引用 SkillWeaver，related work 的覆盖有明显缺口。
- [[Papers/2606-SkillMemoryBudget]] — 方法论上的正面警告。那篇用预算对齐证伪了 AWM / ASI / ReasoningBank 的表面收益，说明**任何"我更省"的 claim 必须做 budget-matched 对照**。本文恰恰缺这一环：它的 baseline 是算出来的，不是跑出来的。若要给本文补一个可信实验，SkillMemoryBudget 的设计是现成模板。
- [[Papers/2511-Prune4Web]] — DSM 的近亲，且本文引用了它。Prune4Web 用 LLM 生成打分参数 + 固定程序遍历剪枝，把候选元素削减 25~50×，并在 Multimodal-Mind2Web 上给出 grounding 精度（46.8% → 88.28%）。对照之下，本文的 DSM "up to 85% 压缩"既无测量也无下游精度验证。
- [[Papers/2504-OnlineMind2Web]] — 本文引用它（Xue et al. 2025）来支持"continuous agent 的 benchmark 成绩不可信、真实环境会崩"，但随后自己采用了不可复现的私有评测。这个引用张力值得在 survey 里点出。

**待查 / 存疑**

- 隐含单价 $3.00 / 1M token 是我按论文自述参数反推的（2,500 × 20,000 = 50M token，$150 / 50M）。论文本身从未写出 C_t，若 verifier 能在正文找到显式定价说明，需修正 C2 的表述。
- Sec 3.4 与 Sec 5.5 关于 automated recompilation 是否已实现的矛盾，值得在引用时明确标注为"实现状态不明"。
- 无 code、无 schema，本篇不适合走 `repo-digest`。
