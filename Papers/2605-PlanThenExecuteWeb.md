---
title: "Web Agents Should Adopt the Plan-Then-Execute Paradigm"
authors: ["Julien Piet", "Annabella Chow", "Yiwei Hou", "Muxi Lyu", "Sylvie Venuto", "Jinhao Zhu", "Raluca Ada Popa", "David Wagner"]
institute: ["UC Berkeley"]
date_publish: 2026-05-14
venue: arXiv
tags: [web-agent, gui-agent, task-planning]
url: https://arxiv.org/abs/2605.14290
arxiv_id: "2605.14290"
doi:
cite_key: piet2026web
code:
rating: 4
content_scope: full-text
verification_status: partial
date_added: 2026-08-10
---
## Summary

Position paper：主张 web agent 应把 plan-then-execute（PTE）而非 ReAct 作为默认架构——先基于站点 trusted API 生成一段控制流预先固定的程序，再交给 executor 执行，使不可信网页内容只能影响数据流、无法改写控制流。作者对 WebArena 860 个任务做人工静态分类，得出全部任务都能用 PTE 表达、其中 699 个（81.28%）连 runtime LLM subroutine 都不需要，并把主要障碍归到基础设施（缺少语义清晰、强类型的站点 API）而非模型能力。

## Problem & Motivation

**为什么 ReAct 对 web agent 是错误的默认值——控制流与信任边界的论证。** 论文的核心不是"ReAct 效果不好"，而是"ReAct 把信任边界画错了位置"。网页内容天然混合多方输入：站点自身的界面元素、用户评论、商品 review、论坛帖、广告、嵌入 widget、生成式推荐、隐藏 DOM 节点、accessibility metadata、渲染图像。因此"untrusted content is pervasive in the agent's ordinary observation stream"——不可信内容不是从少数几个显式通道进来的例外，而是常规 observation stream 的组成部分。这与多数 tool-calling 场景不同：在 web 上攻击者无需攻破网站或用户，只要在 agent 大概率会读到的地方发布内容即可。

而 ReAct 的循环结构恰好把这堆内容送到最危险的位置：`obs = observe_page(); act = LLM(goal, history, obs)`。攻击者控制的 token 出现在模型决定"点什么、输入什么、提交什么、复制什么、访问什么"的同一次 inference 里，而此时 agent 往往带着用户的登录权限。作者用 **confused deputy** 概括：observation 与 action selection 被压缩进一次推理，于是 "runtime observations are not just data consumed by a fixed program; they help determine the program's control flow"。这是架构缺陷，不是模型鲁棒性能补的洞——论文明确把 model-centric defense（instruction hierarchy、StruQ、SecAlign、Jatmo）和 runtime monitor 归为"缓解具体攻击但不触及核心架构缺陷"。

对应地，PTE 把边界重画为程序语义里的 control flow / data flow 分离：untrusted 内容可以填参数、决定既有分支走向、影响 quarantined LLM subroutine 的输出，但 "cannot add steps, remove steps, insert new branches, select new tools, or trigger replanning"。用传统程序类比，control-flow hijacking 相当于任意代码执行（可控 `eval` 输入），outcome manipulation 相当于 data-only attack（只改既有控制流图上走哪条路）。PTE 按设计消除前者，不消除后者。

**第二条批评是效率（论文未量化）。** ReAct 是 near-sighted 的：只能从当前 state 出发，看不到当前页面之外的动作，导致 planning 变成隐式且连续的逐步重推，抬高 token、latency、cost，且早期误步会改变后续观察到的页面从而放大误差。但很多 web 任务（找商品下单、发帖、建改 issue）结构固定可复用，ReAct 却每次都要重新发现同一套 workflow。

**Threat model。** 只考虑 indirect prompt injection；攻击者是网站的第三方（评论者、reviewer、广告主、卖家、论坛用户、issue 作者）；模型提供方与网站所有者被视为可信。攻击目标分 control-flow hijacking 与 outcome manipulation 两类。能同样欺骗人类的普通虚假/误导内容明确不在范围内。

## Method

**Preprocessing：把网站编译成 trusted API。** PTE 要求 planner 在不看 runtime 内容的前提下写出完整程序，因此需要网站动作空间的一个"扁平表示"——一组有文档、有输入输出 schema 的 typed tools。要求两条：**complete**（覆盖网站上所有可做的动作，可以是低层函数如翻页/点按钮，也可以是端到端 workflow 级动作如"搜索并一次返回全部结果"）与 **strongly typed**（price/status/identifier 等字段 schema 稳定，才能把函数串成可校验、可重放的程序）。获取途径有二：(1) **Website-Provided Interface**——站点自带 REST/MCP 接口，但 PTE 需要的信息多于"可调用端点清单"，必须包含类型、参数、返回值、语义与副作用；(2) **Client-Side SDK**——站点没有合适接口时由 agent 开发者预先构建，每个函数用 Playwright 驱动 headless browser 走完一串 UI 动作，或直接发 URL 请求并解析。SDK 是每站一次的"编译"，站点变更才重做。注意这层接口属于 TCB：论文承认 LLM 自动生成 SDK（点名 libretto.sh、skyvern.com）会把 preprocessing 阶段暴露给注入攻击，因此生成的 SDK 需要可信校验或审计。

**Planning。** planner 只拿 task specification 与站点接口，**不接收 runtime 内容**，产出一段控制流图预先确定的程序。

**Execution。** executor 跑预先提交的 plan；runtime 数据可填参数、实例化 typed 变量、影响返回给用户的输出，但不能增删步骤、插入分支、选择新工具或触发 replanning。作者额外指出一个副产品：固定执行图使得**在观察任何不可信内容之前**就能做静态安全审计与策略执行，这在 ReAct 下不可能。

**Expressivity：LLM subroutines 作为 security/utility 折中点。** 两个极端分别是"允许调用任意 sub-agent 并执行其输出"（等价于退化回 ReAct）与"只能生成纯确定性程序"（对注入完全鲁棒但 utility 差）。论文选的 operating point 是：程序主体确定性，但可调用 LLM 做局部变换（extraction、normalization、classification）；关键约束是这些 subroutine **不能产出可执行代码**，输出有显式类型与 schema、永不被解释为指令、只能作为其他函数的输入。示例：`summary ← LLM_extract(text), Submit(summary)`。风险是 subroutine 可被网页内容 poison 而给出错误结果（如把无效 PR 判成有效），但攻击面被限制在"值"上，无法扩张动作集合。论文也明确 LLM subroutine 补不了 API 的缺口：API 缺能力的任务在这个框架里就是表达不出来。

**Task taxonomy（三类）。** *Safe*：可完全表达为 planner 用 trusted API 生成的静态代码，runtime 不用语言模型，对注入 by design 安全，且 plan 可复用缓存。*Safe with Influence*：runtime 需要 LLM subroutine 处理数据，但可约束成具体 plan；结果可被注入影响，但免于任意 control-flow hijacking。*Replan-Needed*：依赖数据驱动的 plan 生成（如"读我的邮件并完成里面所有 action item"），不适合 PTE。

## Key Results

**这是纯静态任务分析，没有跑任何 agent。** 论文原文为 "We manually categorize each task using our taxonomy"，且显式声明假设 "we assume complete and trusted APIs are available for every website, whether provided by websites or built separately"。全文**没有报告任何 success rate、accuracy、token 数、latency 或成本数字**，也没有 ReAct 与 PTE 的对照实验。Section 7 关于"PTE lowers token cost and latency"的说法是未量化断言。

**WebArena 分类结果（Table 1，共 860 个任务，六个站点）：**

| Website | Total | Safe | Safe+Influence | Replan Needed | Viable w/ PTE |
|:--|--:|--:|--:|--:|--:|
| OneStopShop | 192 | 154 (80.21%) | 38 (19.79%) | 0 | 100.00% |
| Wikipedia | 23 | 2 (8.70%) | 21 (91.30%) | 0 | 100.00% |
| Reddit | 129 | 106 (82.17%) | 23 (17.83%) | 0 | 100.00% |
| Map | 128 | 101 (78.91%) | 27 (21.09%) | 0 | 100.00% |
| GitLab | 204 | 185 (90.69%) | 19 (9.31%) | 0 | 100.00% |
| CMS | 184 | 151 (82.07%) | 33 (17.93%) | 0 | 100.00% |
| **Total** | **860** | **699 (81.28%)** | **161 (18.72%)** | **0** | **100.00%** |

即：分母是 WebArena 全部 860 个任务；"纯程序化 plan、无 runtime LLM subroutine" 的是 699/860 = 81.28%；replan-needed 为 0，故 100% 与 PTE 兼容。站点间方差很大——Wikipedia 只有 8.70% 属 Safe（任务本质是文本抽取），GitLab 高达 90.69%（动作高度结构化）。需要 LLM subroutine 的三类原因：语义理解（review 情感）、用背景知识把欠定查询映射到具体值（Liberty Bell City → Philadelphia）、主观匹配（选"最好的" GAN repo）。

**abstract 数字口径不一致（值得留意）。** arXiv 元数据摘要是过期版本，写 "80% can be completed with a purely programmatic plan"；论文 HTML 版摘要写 "81.28%"；正文 Section 6.2 自己也用 "over 80% of tasks are safe / The remaining 20%" 的粗口径。Table 1 精确值 699/860 = 81.28%，以正文表格为准。

**PTE 的主要障碍——论文自己的说法分两层。** 摘要层面只点一个 *main barrier*，且强调它是**基础设施问题而非建模问题**：工具必须干净地映射到语义动作、副作用在执行前已知，agent 才有足够信息去 plan；而 web 不天然暴露这种接口——`click`/`type`/`scroll` 的含义依赖当前页面，在这一层做 planning 必然 near-sighted（只看得见当前页面上的动作，后续动作要先动作才出现）。解法是 typed interface，把网站交互从点击键盘提升到 task-level operation。

Section 6.3 + Appendix B 把它拆成四条 practical gap：

1. **API discoverability**：单个 server 可暴露成百上千端点，跨站任务会迅速超出 context window，且大工具集本身会降低选对端点的能力。作者报告实操中把每个 server 的 API surface 表示成 Swagger 2.0 JSON 效果最好：先定位相关 server → 打开对应 JSON → 先给端点摘要的压缩表示 → 选定后再灌入完整 schema。试过 GraphQL 反而更差（深层且常循环的嵌套查询掩盖了原始参数与返回类型）。
2. **Documentation quality**：没有对功能、签名、参数语义、返回结构与类型的文档，端点"存在但不可用"。还需要站点特有约定：OneStopShop 搜索要用 `%` 而非空格填充词间、Postmill REST API 每个请求都要带 `X-Experimental-API` 头、GitLab 用 `namespace/repo` 标识仓库。
3. **API coverage 不完整 / client-side SDK 脆弱**：WebArena 的 Postmill 只暴露 **16 个 REST API**，用它们只能完成 **33% 的 129 个 Postmill 任务**；即便 GitLab 这种暴露数百 API 的平台，仍有只能走 UI 的任务（如生成 RSS token）。退路是 Playwright SDK，但需要预先（可能带登录态的）站点探索阶段、每次 UI 变更都要维护，且探索不可信服务器本身有安全风险。
4. **缺少显式 error handling**：PTE 把反馈推迟到执行之后，看不到中间信号（如空搜索结果）并据此调整。举例：用户把 "furniture" 拼成 "furnture"，PTE agent 会照字面搜索、无结果后直接终止；ReAct 会察觉拼写问题并迭代改写查询。三条缓解思路：规划前多轮追问澄清歧义任务、训练/提示模型产出带 retry 逻辑的健壮代码、对幂等任务生成多个候选 plan 并行执行后择优。

Section 7 另外列出的 tradeoff 与边界：preprocessing 成本高且如何组织 API 才最优尚不清楚；API 需随网站演进维护（ReAct 没有这项成本）；PTE 只支持控制流能完全由用户 prompt 决定的任务；plan 抽象层级要拿捏（太低层脆弱、太高层隐藏执行所需信息）。作者点名三种 **ReAct 更优**的情形：结构频繁变化的高动态网站、需要在规划期依赖外部数据的探索型任务、跨多站点且部分站点未预处理的 workflow；建议默认 PTE、不利情形回落 ReAct。

**安全性收益是定性论证，非实测。** PTE 按设计消除第三类风险（改写 plan 本身的注入）；但 safe-with-influence 任务仍暴露于前两类——普通误导性内容（作者认为这是信息完整性问题而非 agent 安全问题）与 outcome manipulation（如 Reddit 任务"找只推荐一本书的帖子"中，一个提及多本书但措辞使某本显得唯一的帖子会被误选）。论文强调此时"damage is bounded"。Appendix A Table 2 把 safe-with-influence 的影响模式按站点归类（OneStopShop 38 例语义商品筛选/review 提及抽取、Wikipedia 21 例内容依赖抽取、Reddit 23 例帖子筛选、Map 27 例知识解析与主观排序、GitLab 19 例 MR 评论解读与主观仓库选择、CMS 33 例情感聚合与审核动作）。全程无任何攻击成功率或防御有效性的实测数字。

## Evidence Ledger

> 状态来自一次独立 verifier pass（只给 primary source、claim package 与状态定义，不给本笔记的分析与优缺点判断）。`source-verified` 仅表示原文确实包含该信息，不表示结果已被独立复现。

> 本轮为 prepare-only，Finder 不得自判 `source-verified`；下列 Status 一律为 `pending`，待独立 verifier 复核后由 coordinator 落定。locator 与 excerpt 均取自 arXiv:2605.14290v1 HTML 全文。

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | WebArena 全部 860 个任务均被判定与 PTE 兼容，replan-needed 为 0 | number | Sec 6.2, Table 1 | "Total \| 860 \| 699 (81.28%) \| 161 (18.72%) \| 0 \| 100.00%" | source-verified |
| C2 | 699/860 = 81.28% 的任务可由纯程序化 plan 完成，无需任何 runtime LLM subroutine | number | Sec 6.2, Table 1 | "81.28% can be completed with a purely programmatic plan, without any runtime LLM subroutine" | source-verified |
| C3 | arXiv 元数据摘要为过期版本（写 80%，且缺 "platform-generated recommendations" 与结尾的 research-agenda 句）；HTML 摘要与 Table 1 写 81.28%；§6.2 正文本身用 "over 80% / remaining 20%" 粗口径 | number | arXiv abs page vs. HTML Abstract vs. §6.2 | abs 页："while 80% can be completed with a purely programmatic plan"；§6.2："over 80% of tasks are safe" | source-verified |
| C4 | Table 1 的分类是人工静态标注，未跑 agent 得出；论文假设每个网站都有完整可信 API。Appendix B 报告了 planner 的定性试验（Swagger 2.0 优于 GraphQL），但无任何量化结果 | benchmark-setting | Sec 6.2 "Assumptions" / "Results"；Appendix B Obs 1 | "We manually categorize each task using our taxonomy"; "We assume complete and trusted APIs are available for every website"; "representing each server's API surface as a Swagger 2.0 JSON file worked best… causing the agent to struggle" | source-verified（原表述"未运行任何 agent"过宽，已按独立 verifier 意见收窄） |
| C5 | 全文未报告任何 accuracy、success rate、token 或 latency 数字；效率收益仅为断言 | number | Sec 7 Discussion（全文negative check） | "It lowers token cost and latency by allowing the model to plan an efficient execution strategy" | source-verified |
| C6 | 站点级 Safe 比例方差大：Wikipedia 8.70%（2/23）最低，GitLab 90.69%（185/204）最高 | number | Table 1 | "Wiki \| 23 \| 2 ( 8.70%)"; "GitLab \| 204 \| 185 (90.69%)" | source-verified |
| C7 | WebArena 的 Postmill 仅暴露 16 个 REST API，仅 33% 的 129 个 Postmill 任务可由其完成 | number | Sec 6.3 Obs 3 / App B Obs 3 | "only 16 REST APIs are exposed... with only 33% of 129 tasks doable" | source-verified |
| C8 | PTE 的核心安全属性：runtime 观察不能增删步骤、插入分支、选新工具或触发 replanning | causal-mechanism | Sec 4.2 "Execution" | "runtime observations cannot add steps, remove steps, insert new branches, select new tools, or trigger replanning" | source-verified |
| C9 | ReAct 的缺陷被论证为架构性的：注入 token 恰好出现在模型选择下一动作之处，构成 confused deputy | causal-mechanism | Sec 1, Sec 3 "Insecure" | "attacker-controlled tokens appear at exactly the point where the model chooses what to do next" | source-verified |
| C10 | PTE 消除 control-flow hijacking，但 safe-with-influence 任务仍暴露于 outcome manipulation | causal-mechanism | Sec 6.2 "Discussion" | "adversary can influence a decision point, but cannot induce actions outside the plan" | source-verified |
| C11 | 摘要认定主障碍是基础设施而非建模：浏览器 click/type/scroll 语义依赖页面 | causal-mechanism | Abstract | "This is an infrastructure problem, not a modeling problem" | source-verified |
| C12 | 论文自认 ReAct 在三种情形下更优：高动态站点、探索型任务、跨多站点 workflow | comparison | Sec 7 Discussion | "ReAct is superior in three cases: on highly dynamic websites...; exploration-heavy tasks...; workflows spanning many websites" | source-verified |
| C13 | 八位作者均来自 UC Berkeley；arXiv 提交日 2026-05-14；无代码仓库链接 | license-code | arXiv abs page / HTML author block | "[Submitted on 14 May 2026]"; 全部 affiliation 为 "UC Berkeley" | source-verified |

## Strengths & Weaknesses

**Strengths.** 论证的层级选得对。这篇没有停在"ReAct 容易被注入"这种现象描述上，而是把问题重述为程序语义里的 control flow 与 data flow 未分离，于是防御目标从"让模型更鲁棒"（一个开放性的、攻击者总能再走一步的博弈）变成"让不可信数据物理上无法出现在控制流决策点"（一个可静态检查的结构性质）。这个重述让"执行前做安全审计"从愿望变成可能，是它比 model-centric defense 与 runtime monitor 更有力的地方。

任务普查这件事本身也有价值。以往关于"web agent 需要多少反应性"的讨论多停留在直觉，这篇给了一个逐任务的、可复核的分母（860）与分类结果，并且诚实地把站点方差摆出来——Wikipedia 8.70% vs GitLab 90.69% 的巨大差距，恰恰说明"多少任务需要反应性"根本不是一个 web 的常数，而是站点动作空间结构化程度的函数。这比 81.28% 这个总数更有信息量。

**Weaknesses.** 最大的问题是**证据与主张之间的落差**。论文题目是规范性的（"should adopt"），但支撑它的全部经验证据是一次人工任务分类，外加 Appendix B 里几段没有数字的 planner 试用观察。全文不含任何 success rate、token 或 latency 数字，这意味着以下问题全部未被触及：planner 在真实 API 面前能否写出正确程序、程序的一次通过率是多少、PTE 与 ReAct 在同一批任务上的 success rate 差多少、宣称的 token/latency 收益究竟多大。论文自己在 research agenda 里把这些列为 future work，态度是诚实的，但读者不应把 "81.28% 的任务可以用 PTE 表达" 读成 "81.28% 的任务 PTE 能做对"——前者是可表达性上界，后者是端到端能力，二者之间隔着整个 planner 与 SDK 的实现质量。

第二，**核心假设吞掉了核心困难**。"assume complete and trusted APIs are available for every website" 这一句让 100% 这个数字变得近乎重言：只要 API 完整，任何确定性任务当然都能写成程序。而论文自己给的 Postmill 数据（16 个 REST API，33% 覆盖）恰好说明这个假设离现实有多远。真正该被测量的量不是"假设 API 完整时有多少任务可 PTE"，而是"在真实 API 覆盖率下有多少任务可 PTE"，后者这篇只给了一个站点的点估计，且是 33% 而非 81%。这两个数字在读者脑中很容易被混淆，论文对这层落差的处理略显轻描淡写。

第三，**分类是单标注、无 inter-annotator agreement**。"这个任务需不需要 LLM subroutine" 在很多边界情形上是判断题（论文举的"选最好的 GAN repo"就是），完全依赖作者对"可用 API 长什么样"的想象。没有第二标注者、没有一致性统计、没有公开分类结果，81.28% 的误差棒无从判断。

第四，**preprocessing 的安全性被推给了未来**。TCB 里放进了一个可能由 LLM 从不可信站点自动生成的 SDK，论文承认"exposes the preprocessing stage to injection attacks"并要求"trusted validation or auditing"，但没有说这个审计怎么做、成本多大。攻击面可能只是从 runtime 迁移到了 build time，而不是消失。同理，quarantined LLM subroutine 的输出虽然不被当作指令，但当它决定一个 `if` 分支时，它与控制流的距离究竟有多远，论文用"damage is bounded"带过，缺少形式化刻画。

**对领域的意义。** 放在 agent harness 设计的坐标系里，这篇的贡献是把 loop structure 的选择从"工程口味"提到了"安全属性"的高度，并且给出一个明确的可证伪断言——web 任务默认不需要反应性，需要的是 typed, complete, auditable 的站点 API。它与 API-based agent 那条线（Beyond Browsing、API vs GUI agents）合流，共同指向"把网站为 agent 重新编译一遍"这个方向。是否成立取决于一个这篇论文没有回答的经验问题：为长尾网站构建并维护可信 API 的成本，是否低于让 ReAct agent 变得足够安全的成本。

## Mind Map

```mermaid
mindmap
  root((PlanThenExecuteWeb))
    Problem
      ReAct 把不可信内容送进动作决策点
      confused deputy 架构缺陷
      near-sighted 导致重复 replan
      威胁模型 第三方 indirect injection
    Method
      Preprocessing 造 trusted API
        website-provided interface
        client-side Playwright SDK
      Planning 不接触 runtime 内容
      Execution 控制流固定
      LLM subroutines 作为折中点
      Taxonomy Safe / Safe-with-Influence / Replan-Needed
    Results
      860 任务 100 pct 与 PTE 兼容
      699 任务 81.28 pct 纯程序化
      站点方差 Wiki 8.70 vs GitLab 90.69
      Postmill 16 个 API 覆盖 33 pct
      纯静态分析 无 agent 运行
    Limits
      主障碍 基础设施非建模
      API 发现 / 文档 / 覆盖 / 错误处理
      无 accuracy 无 token 数字
