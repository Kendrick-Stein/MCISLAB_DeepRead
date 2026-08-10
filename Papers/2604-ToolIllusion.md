---
title: "The Tool Illusion: Rethinking Tool Use in Web Agents"
authors: [Renze Lou, Baolin Peng, Wenlin Yao, Qianhui Wu, Hao Cheng, Suman Nath, Wenpeng Yin, Jianfeng Gao]
institute: ["Microsoft Research, Redmond", "The Pennsylvania State University, University Park"]
date_publish: 2026-04-03
venue: "COLM 2026"
tags: [web-agent, gui-agent, task-planning]
url: "https://arxiv.org/abs/2604.03465"
arxiv_id: "2604.03465"
doi: ""
cite_key: lou2026tool
code:
rating: 4
content_scope: full-text
verification_status: verified
date_added: "2026-08-10"
---
## Summary

在 WALT、SkillWeaver、Hybrid-Agent 三套 tool-use web agent framework 上用同一组五个 backbone 跑 WEBARENA 与 VISUALWEBARENA，结论是工具收益并非无条件：人工编写的 REST API 对五个 backbone 全部有效（WEBARENA 上最高 +19.6pp），而 LLM 合成的工具只在使用者明显弱于合成者时稳定有效，GPT-5 用 WALT 的工具反而从 52.9 掉到 50.9。作者进一步反驳"工具越全越好"的直觉：SkillWeaver 62% 的工具属于高复杂度，79% 在整个 benchmark 上一次都没被调用。工具还同时抬高 token 成本与动作步数，Hybrid-Agent 的每站点平均 token 从 10.5M 涨到 33.9M、平均步数从 7.1 涨到 8.3。

## Problem & Motivation

Web agent 的动作面正在从 click/type 一类原子浏览器操作上移到工具，也就是 API 或封装好的过程函数。一次工具调用可以顶掉一长串页面交互，因此这条路线被普遍视为对低层交互的改进。

问题在于支撑它的证据太薄。既有工作通常只用单一 tool source（比如只由一个模型合成工具），只在同一模型家族的少数 backbone 上评测，结论之间因此互相打架：Zheng et al. (2025) 用 GPT-4o 合成工具、只在 GPT-4o 与 GPT-4o-mini 上评，得出"弱模型从工具中获益更多"；Prabhu et al. (2025) 换了 tool source 和 backbone 集合，报告的趋势相反。两个结论都不是错的，但都不足以支撑"工具有用"这个一般命题，也无法告诉后来者工具在什么条件下失效。

作者据此提出三个问题：工具（尤其是 LLM 合成的工具）是否稳定优于纯浏览器 agent，什么条件下失效；有效工具的设计原则是什么；工具相对低层交互引入了什么代价与副作用。

## Method

这是一篇受控实证研究，没有提出新方法，贡献在对照设计上。

**被比较的四个 framework。** 论文用 Table 1 对齐了四套框架的设计选择，实验只取前三套（都开源、都以 WEBARENA 为下游、但工具设计差异极大）。WebMCP 只作为对照列出。

| | Hybrid-Agent | SkillWeaver | WALT | WebMCP |
|:--|:--|:--|:--|:--|
| Web observation | Axtree + DOM | Axtree + Screenshot | DOM + Screenshot | – |
| Tool source | Human | LLM 合成（GPT-4o） | LLM 合成（GPT-5-mini） | Human |
| Tool format | REST API（HTTP） | Python 函数（Playwright） | JSON UI action flow（Playwright） | JS callback API（站点内置） |
| Tool UI selector | – | A11y role selector | DOM selector + XPath + ElementHash | – |
| 每站点平均工具数 | 437 | 88 | 8 | – |

Hybrid-Agent 来自 Song et al. (2025)，为 WEBARENA 站点收集了两千余个人工开发的 API；SkillWeaver 让 agent 自提任务、把可复用轨迹封装成函数，为 WEBARENA 生成四百多个工具；WALT 用更鲁棒的选择器并把繁琐的 UI 序列替换成直接的 URL 操作，刻意做小工具集。

**评测面。** WEBARENA 取五个单站点子集，Shopping 187、CMS 182、GitLab 180、Reddit 106、Map 109，排除跨站点任务（因为 SkillWeaver 的工具是为单站点设计的）。VISUALWEBARENA 取 Classifieds 234、Shopping 466、Reddit 210。两者都用二值成功率。Backbone 跨三个模型家族：GPT-5、GPT-5-mini、GPT-5-nano、Grok-4.1-Fast-Reasoning、Mistral-Large-3.1。

**哪些设置对齐了，哪些没有。** 对齐的部分：所有 agent 温度设 0，reasoning effort 保持默认的 medium；同一 framework 内 w/ tools 与 w/o tools 只切换工具可用性；WALT 原本用 GPT-5 做 visual planner、GPT-5-mini 做 browser agent，作者改成两者同模型，以免模型规模变量被混淆。没有对齐的部分同样重要：三套 framework 的 web observation 格式不同（Hybrid-Agent 直接拼接扁平化 DOM 与 accessibility tree 后简单截断，原生不用截图；另两套用简化的单一结构化表示加截图），并且"其余生成参数一律沿用各 framework 官方仓库的默认值"，论文没有报告统一的 max-step 或 token 上限。因此**跨 framework 的 tool gain 数值不可直接相比**，可比的是同一 framework 内部沿 backbone 与沿 tool constructor 两个方向的变化。

**两个方向的 scaling。** Table 2-4 固定 tool developer、扫 tool user；Table 5 反过来固定 tool user、用不同模型重跑各 framework 的工具合成流程。后者因为合成成本高，只做了两个站点：SkillWeaver 取 CMS、WALT 取 Reddit，选择理由是这两处"用工具前后的分数趋势最明显"。

**两个附加对照。** 一是把 SkillWeaver 的 Python 工具函数用 GPT-4.1 翻译成自然语言 skill（保留过程步骤与前置条件，去掉选择器和代码细节），以高层指导而非可执行调用的形式给 agent，用来分离"过程性知识"与"可执行封装"两件事。二是视觉消融：对原本就用截图的 WALT 与 SkillWeaver 去掉截图，对原本纯文本的 Hybrid-Agent 反向注入截图。

**工具复杂度的操作化。** 分 high / medium / low 三级。WALT 与 SkillWeaver 的 Python 函数由 GPT-4.1 按 prompt 判级，判据是交互步数与控制逻辑：high 是端到端、过度具体的任务（如 `search_product_and_change_price`，通常 8 步以上或含循环/条件），medium 是聚焦的子任务（如 `search_product`，通常 5 步以上但逻辑简单），low 是原子操作（如 `navigate_to_orders_page`，5 步以内无复杂逻辑）。Hybrid-Agent 的 REST API 数量太大，改用基于 API 文档的启发式规则，看 HTTP method、文档关键词隐含的语义范围、显式参数个数、以及文档描述的是单个 endpoint 还是多步 workflow。

## Key Results

**Q1：人工工具稳定有效，合成工具不是。** Hybrid-Agent 开启工具后五个 backbone 在两个 benchmark 上全部上涨，WEBARENA 平均涨幅在 +12.4 到 +19.6pp 之间（GPT-5-mini 从 19.3 到 38.9 最大），VISUALWEBARENA 在 +3.4 到 +8.2pp。作者归因于站点原生 REST API 的高可靠性与广覆盖。WALT 与 SkillWeaver 则给出混合结果。

| Framework | Backbone | WEBARENA w/o → w/ | VISUALWEBARENA w/o → w/ |
|:--|:--|:--|:--|
| WALT（工具由 GPT-5-mini 合成） | GPT-5 | 52.9 → 50.9（↓2.0） | 52.8 → 51.9（↓0.9） |
| | GPT-5-mini | 46.2 → 46.0（↓0.2） | 46.0 → 47.6（↑1.6） |
| | GPT-5-nano | 24.4 → 28.6（↑4.2） | 23.9 → 31.0（↑7.1） |
| | Grok-4.1-R | 44.5 → 46.6（↑2.1） | 43.9 → 44.7（↑0.8） |
| | Mistral-L-3.1 | 35.3 → 40.2（↑4.9） | 38.5 → 41.0（↑2.5） |
| SkillWeaver（工具由 GPT-4o 合成） | GPT-5 | 39.2 → 37.4（↓1.8） | 37.9 → 34.4（↓3.5） |
| | GPT-5-mini | 26.0 → 27.3（↑1.3） | 25.9 → 24.3（↓1.6） |
| | GPT-5-nano | 11.0 → 13.1（↑2.1） | 11.2 → 13.2（↑2.0） |
| | Grok-4.1-R | 32.8 → 30.4（↓2.4） | 33.2 → 29.6（↓3.6） |
| | Mistral-L-3.1 | 23.6 → 22.9（↓0.7） | 22.3 → 20.6（↓1.7） |
| Hybrid-Agent（人工 REST API） | GPT-5 | 36.5 → 49.9（↑13.4） | 32.0 → 35.4（↑3.4） |
| | GPT-5-mini | 19.3 → 38.9（↑19.6） | 16.0 → 24.2（↑8.2） |
| | GPT-5-nano | 10.1 → 22.5（↑12.4） | 8.9 → 14.4（↑5.5） |
| | Grok-4.1-R | 26.2 → 42.7（↑16.5） | 25.5 → 29.5（↑4.0） |
| | Mistral-L-3.1 | 16.6 → 31.2（↑14.6） | 11.7 → 17.6（↑5.9） |

作者据此提出的规则是相对强弱而非绝对规模。WALT 的工具由 GPT-5-mini 合成，而 GPT-5-mini 恰好是 Table 2 中第二强的 backbone；所有基线弱于它的模型都稳定受益，它自己收益微弱，比它强的 GPT-5 反而下降。SkillWeaver 的工具由 GPT-4o 合成，Zheng et al. (2025) 报告的 GPT-4o WEBARENA 无工具成绩是 22.6%，Table 3 中只有 GPT-5-nano（11.0）明显低于这个参照点，也只有它在两个 benchmark 上都稳定获益。论文用脚注明确承认强弱是 framework 相关而非绝对的：Grok-4.1-R 在 Table 3 中强于 GPT-5-mini，在 Table 2 中顺序反过来。

**Q1 补充：反方向 scaling 同样成立。** Table 5 固定 tool user、换 tool constructor，SkillWeaver 用 CMS、WALT 用 Reddit。

| | GPT-5 | GPT-5-mini | GPT-5-nano |
|:--|:--|:--|:--|
| SkillWeaver 基线（CMS） | 43.4 | 25.3 | 9.9 |
| 工具 by GPT-4o | ↓42.9 | ↑28.6 | ↑12.1 |
| 工具 by GPT-5-mini | ↓41.8 | ↑29.7 | ↑16.5 |
| 工具 by GPT-5 | ↑44.5 | ↑31.3 | ↑17.6 |
| WALT 基线（Reddit） | 47.4 | 38.6 | 17.5 |
| 工具 by GPT-4o | ↓37.7 | ↓31.6 | ↑24.6 |
| 工具 by GPT-5-mini | ↓39.5 | ↓33.3 | ↑27.2 |
| 工具 by GPT-5 | ↑48.2 | ↑43.0 | ↑29.8 |

明显弱于所有 constructor 的 GPT-5-nano 在六种组合下全部获益；GPT-5-mini 只在 constructor 是 GPT-5 时可靠获益；GPT-5 只有在工具由自己合成时才不掉分。作者把这个模式称为单向的 capability distillation。

**Q2：更全的工具不等于更好。** 工具复杂度分布上，SkillWeaver 有 62%（272 个）属于 high，WALT 只有 7%（3 个），Hybrid-Agent 只有 4%（73 个）。SkillWeaver 激进地封装深层轨迹，导致工具内含循环与条件判断、强依赖特定 UI 状态，过度任务专用。后果直接反映在调用分布上：SkillWeaver 79%（341 个）的工具在整个 WEBARENA 评测中一次都没被调用，WALT 是 22%（9 个），Hybrid-Agent 是 20%（389 个）。作者称之为无效的 scaling——工具集规模没有转化为等比例的实际效用。

**Q3：真正起作用的是功能覆盖与可组合性。** Table 6 按任务实际用到的工具数分组：

| | WALT 任务数 / 成功率 | SkillWeaver | Hybrid-Agent |
|:--|:--|:--|:--|
| 0 tools | 357（45%）/ 56.3% | 159（21%）/ 42.1% | 82（11%）/ 39.0% |
| 1 tool | 291（37%）/ 43.6% | 408（54%）/ 39.2% | 286（37%）/ 50.3% |
| ≥2 tools | 140（18%）/ 32.1% | 194（25%）/ 27.5% | 396（52%）/ 41.2% |

Hybrid-Agent 有 52% 的任务通过多工具组合完成，且这批任务的成功率（41.2%）明显高于另两套框架的对应格（32.1% 与 27.5%）；只有 11% 的任务退回纯浏览器操作，说明工具集对 WEBARENA 的任务意图覆盖较全。WALT 呈相反态势，45% 的任务仍靠纯浏览器交互，覆盖有限。论文由此给出的设计原则是：工具不必端到端一次解决任务，接近原子操作的低层工具也可以接受，前提是它们能可靠组合并共同覆盖高频用户意图。

**Q4：工具带来隐性税。** 每站点平均 token 成本在三套框架上开启工具后都上升，Hybrid-Agent 因为工具库极大而涨幅最猛。

| | w/o tools（prompt / completion / reasoning） | w/ tools |
|:--|:--|:--|
| WALT | 14.5M（11.0 / 2.0 / 1.5） | 16.3M（12.9 / 1.9 / 1.5） |
| SkillWeaver | 11.6M（6.1 / 3.6 / 1.9） | 19.5M（11.9 / 4.6 / 3.0） |
| Hybrid-Agent | 10.5M（5.8 / 2.7 / 2.0） | 33.9M（22.1 / 6.9 / 4.9） |

动作效率上只有 WALT 变快（10.2 → 9.3 步），SkillWeaver 基本持平（7.3 → 7.2），Hybrid-Agent 反而变慢（7.1 → 8.3）。作者归因于工具集规模与工具效用：Hybrid-Agent 的巨大工具库迫使 agent 花额外步数做检索、选择与查验；SkillWeaver 的工具则因过度任务专用而引发错误调用与参数反复调整，agent 需要花步数从工具报错中恢复。论文提到工具合成本身也有不小开销，但没有量化。

**Q5：semantic skill 是可行替代，但依赖 backbone 能力。** 把 SkillWeaver 的 Python 工具翻译成自然语言 skill 后，在 CMS 上 GPT-5 拿到 45.1，高于无工具基线 43.4 和用工具的 42.9；Reddit 上 skill 34.9，同样高于基线 31.1 和工具 30.2。GPT-5-nano 的方向相反：CMS 上 skill 只有 9.3，低于基线 9.9，而工具是 12.1；Reddit 上 skill 10.4 低于工具 11.3。作者的解释是 skill 的白盒性让强模型可以检视、部分遵循、修改或忽略这些过程知识，容错空间比硬编码工具大，但弱模型消化这些知识的负担超过收益。由此给出的实践建议是：预算不足以用强模型合成工具时，把弱模型生成的工具翻译成 skill，对推理能力足够的 backbone 反而更划算。

**Q6：视觉仍然有用，工具降低对它的依赖。** GPT-5 在 CMS 与 Reddit 上的视觉消融：

| | CMS w/ vision → w/o | Reddit w/ vision → w/o |
|:--|:--|:--|
| WALT w/o tools | 52.2 → 46.2（↓6.0） | 47.4 → 37.7（↓9.7） |
| WALT w/ tools | 57.1 → 50.0（↓7.1） | 39.5 → 36.8（↓2.7） |
| SkillWeaver w/o tools | 43.4 → 37.4（↓6.0） | 31.1 → 26.4（↓4.7） |
| SkillWeaver w/ tools | 42.9 → 38.5（↓4.4） | 30.2 → 28.3（↓1.9） |
| Hybrid-Agent w/o tools（反向注入截图） | 39.6 → 46.7（↑7.1） | 38.7 → 42.5（↑3.8） |
| Hybrid-Agent w/ tools（反向注入截图） | 50.5 → 52.7（↑2.2） | 57.5 → 58.5（↑1.0） |

去掉视觉在 WALT 与 SkillWeaver 的四个格里都掉分；多数设置下有工具时的视觉缺口小于无工具时（WALT Reddit 从 9.7 收窄到 2.7，SkillWeaver Reddit 从 4.7 收窄到 1.9，CMS 从 6.0 收窄到 4.4；WALT CMS 是例外，6.0 扩大到 7.1）。反向注入截图的 Hybrid-Agent 呈同一模式：无工具时注入视觉的增益（+7.1 / +3.8）大于有工具时（+2.2 / +1.0）。

**被修订的先前结论。** 论文明确改写了四条既有说法。第一，Krishna et al. (2024)、Song et al. (2025)、Zheng et al. (2025)、Prabhu et al. (2025) 共同呈现的"工具对 web agent 一致有益"被改为条件成立，人工工具一致有益而 LLM 合成工具取决于合成者与使用者的相对强弱。第二，Zheng et al. (2025) 的"弱模型从工具中获益更多"与 Prabhu et al. (2025) 报告的相反趋势被统一解释为同一规则在不同 tool source 下的两种表现，而非模型规模本身的性质。第三，"工具越全面、工具集越大越好"被 62% 高复杂度对应 79% 零调用的证据反驳。第四，"一次工具调用替代一长串浏览器操作因此更高效"这一效率前提在三套框架里只有 WALT 成立。被补充而非推翻的是 Song et al. (2025) 关于混合工具调用与浏览器动作的主张，以及 He et al. (2024)、Kil et al. (2024)、Furuta et al. (2024) 关于视觉输入价值的结论。

**可复现性披露。** Appendix A 列出了为复现三套框架所做的代码修改，包括环境配置、工具注册、benchmark 任务配置、网站登录的 cookie 校验、工具内硬编码 URL、以及 VISUALWEBARENA 缺失视觉素材。Appendix B.1 补充了两条原论文未披露的信息：SkillWeaver 的工具构建流程实际同时用到 GPT-4o 与 o3-mini（前者生成被封装的轨迹，后者用于后续阶段），作者因核心过程来自 GPT-4o 轨迹而在表中仍记为 GPT-4o；WALT 的论文与仓库都没有说明工具由哪个模型构建，作者只能采用其 tool discovery 流程中 `llm_name` 的默认值作为最佳可得证据。模型部署 ID 为 gpt-5_2025-08-07、gpt-5-mini_2025-08-07、gpt-5-nano_2025-08-07、grok-4-1-fast-reasoning、Mistral-Large-3_1，均走 Azure API。

## Evidence Ledger

> 状态来自一次独立 verifier pass（只给 primary source、claim package 与状态定义，不给本笔记的分析与优缺点判断）。`source-verified` 仅表示原文确实包含该信息，不表示结果已被独立复现。

> 本轮为 Finder 起草，尚未派发独立 verifier，所有状态为 `pending-verification`，`verification_status` 相应记为 `unverified`。全文来源为 arXiv PDF v2（arXiv HTML 与 ar5iv 均不可用），locator 按 PDF 页码与图表编号给出。

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | Hybrid-Agent 开启人工 REST API 后，五个 backbone 在两个 benchmark 上全部提升，WEBARENA 涨幅 +12.4 至 +19.6pp | number | p.5, Table 4 | "GPT-5-mini 19.3 → 38.9 (↑19.6); GPT-5-nano 10.1 → 22.5 (↑12.4)" | source-verified |
| C2 | WALT 的 GPT-5-mini 合成工具使 GPT-5 的 WEBARENA 均值从 52.9 降至 50.9、VISUALWEBARENA 从 52.8 降至 51.9 | number | p.4, Table 2 | "GPT-5 52.9 / 50.9 (↓2.0); 52.8 / 51.9 (↓0.9)" | source-verified |
| C3 | SkillWeaver 的 GPT-4o 合成工具下，五个 backbone 中只有 GPT-5-nano 在两个 benchmark 上都提升（11.0→13.1、11.2→13.2） | number | p.4, Table 3 | "GPT-5-nano 11.0 / 13.1 (↑2.1); 11.2 / 13.2 (↑2.0)" | source-verified |
| C4 | 固定 tool user、变 tool constructor 时，GPT-5-nano 在全部六种组合下获益；GPT-5-mini 在 WALT-Reddit 上仅当 constructor 为 GPT-5 才获益（38.6→43.0），但在 SkillWeaver-CMS 上三种 constructor 均带来提升（25.3→28.6/29.7/31.3），故论文"GPT-5-mini 只在 constructor 为 GPT-5 时可靠获益"的概括被其自身 Table 5 部分反驳 | number | p.6, Table 5 | "WALT 38.6; by GPT-4o ↓31.6; by GPT-5-mini ↓33.3; by GPT-5 ↑43.0" | source-verified（例外行由独立 verifier 补出） |
| C5 | LLM 合成工具的收益规则被表述为"仅当 tool user 明显弱于 tool developer 时稳定成立" | causal-mechanism | p.6, §4.1 末段 | "yield consistent gains only when the 'tool user' is clearly weaker than the 'tool developer'" | source-verified |
| C6 | 强弱判定是 framework 相关而非绝对：Grok-4.1-R 在 Table 3 强于 GPT-5-mini，在 Table 2 顺序反转 | benchmark-setting | p.6, 脚注 2 | "'weaker' and 'stronger' are framework-dependent rather than absolute notions" | source-verified |
| C7 | 工具复杂度分布：SkillWeaver high 占 62%（272），WALT 7%（3），Hybrid-Agent 4%（73） | number | p.7, Figure 1 | "SkillWeaver 62% (272); WALT 7% (3); Hybrid-Agent 4% (73)" | source-verified |
| C8 | SkillWeaver 79%（341）的工具在 WEBARENA 评测中零调用，WALT 22%（9），Hybrid-Agent 20%（389） | number | p.7, Figure 2 | "SkillWeaver 79% (341); WALT 22% (9); Hybrid-Agent 20% (389)" | source-verified |
| C9 | Hybrid-Agent 52%（396）任务用 ≥2 工具且成功率 41.2%，WALT 18%（140）/32.1%，SkillWeaver 25%（194）/27.5% | number | p.7, Table 6 | "≥2 tools: 140 (18%) 32.1% / 194 (25%) 27.5% / 396 (52%) 41.2%" | source-verified |
| C10 | 三套框架开启工具后每站点平均 token 成本均上升：14.5M→16.3M、11.6M→19.5M、10.5M→33.9M | number | p.8, Figure 3 | "WALT 14.5M / 16.3M; SkillWeaver 11.6M / 19.5M; Hybrid-Agent 10.5M / 33.9M" | source-verified |
| C11 | 平均步数只有 WALT 下降（10.2→9.3），SkillWeaver 持平（7.3→7.2），Hybrid-Agent 上升（7.1→8.3） | number | p.8, Figure 4 | "WALT 10.2 / 9.3; SkillWeaver 7.3 / 7.2; Hybrid-Agent 7.1 / 8.3" | source-verified |
| C12 | Skill 化后 GPT-5 在 CMS 45.1、Reddit 34.9，均高于基线（43.4 / 31.1）与工具（42.9 / 30.2）；GPT-5-nano 相反，CMS skill 9.3 低于基线 9.9 | number | p.9, Figure 5 | "CMS: 43.4 base, 42.9 tool, 45.1 skill; nano 9.9 / 12.1 / 9.3" | source-verified |
| C13 | 去掉视觉在 WALT 与 SkillWeaver 各四格共八格中全部掉分；六个设置中五个的视觉缺口在有工具时更小（WALT Reddit ↓9.7 → ↓2.7），例外为 WALT-CMS（↓6.0 → ↓7.1） | number | p.10, Table 7 | "WALT w/o tools 47.4 / 37.7 (↓9.7); w/ tools 39.5 / 36.8 (↓2.7)" | source-verified（格数与例外由独立 verifier 更正） |
| C14 | 设置匹配范围：温度 0、reasoning effort 默认 medium 全局统一，其余生成参数沿用各 framework 仓库默认值 | benchmark-setting | p.16, §A.4 | "temperature of all agents to 0... All other generation parameters are kept at the default values specified in each framework's released repository" | source-verified |
| C15 | SkillWeaver 工具实际由 GPT-4o 与 o3-mini 共同构建；WALT 的构建模型在论文与仓库中均未说明，作者用 `llm_name` 默认值推断 | benchmark-setting | p.16-17, §B.1 | "neither the paper nor the released repository explicitly specifies which model was used to construct the tools" | source-verified |
| C16 | 评测子集：WEBARENA 排除跨站点任务，五站点 187/182/180/106/109；VISUALWEBARENA 三站点 234/466/210 | benchmark-setting | p.3-4, §3 与脚注 1 | "Shopping (187), CMS (182), GitLab (180), Reddit (106), and Map (109)... We exclude multi-site tasks" | source-verified |

## Strengths & Weaknesses

**亮点。** 同一 framework 内固定工具集、扫五个跨家族 backbone 这个设计，恰好切开了两篇先前工作纠缠在一起的两个变量（tool source 与 backbone 家族），这是全文最有价值的一步。Table 5 反方向 scaling（固定使用者、重跑合成流程）代价高昂，多数论文会跳过，作者做了并且承认只能覆盖两个站点。工具调用直方图是个廉价却少见的诊断量，把"工具库规模"从一项美德变成一个可测量的负债：79% 从未被调用这个数字，比任何成功率对比都更能说明合成工具的实际效用。Appendix A 逐条列出为复现所做的代码改动，B.1 主动披露 WALT 的构建模型无从考证，这种披露密度在实证对比类论文里高于平均水平。

**跨 framework 比较是混淆的，而论文的归因没有充分处理这一点。** 三套框架的观测格式、工具格式、步数与 token 默认值都不同。GPT-5 在同一 WEBARENA 子集上，WALT 的无工具基线是 52.9，Hybrid-Agent 只有 36.5，harness 本身就差了 16.4pp。论文把 Hybrid-Agent 的 +13.4pp 完全归因于站点原生 REST API 的质量，但从一个明显更弱的 harness 起步、且有更大的提升空间，这两种解释在当前数据下无法分离。一个能分开的最小检验是把 Hybrid-Agent 的观测层换成 WALT 的简化表示后重跑，论文没有做。

**capability distillation 的表述在当前形式下接近不可证伪。** 强弱由 framework 内的基线成绩定义，而这个基线正来自要被解释的同一张表；脚注 2 承认 Grok-4.1-R 的强弱排序在 Table 2 与 Table 3 之间翻转。这意味着任何获益的模型都可以事后被归类为"在该 framework 下更弱"。Table 5 是更有力的证据，因为它沿构建者方向变化，但它只覆盖两个 framework 各一个站点、三个 backbone，而站点选择的理由是"趋势最明显"——这是按结果做的选择。

**§4.1 与 §4.3 给出的是两套解释，论文没有分开它们。** SkillWeaver 的工具同时具备两个特征：由最弱的 constructor 合成，以及 62% 属于高复杂度、强 UI 状态依赖。前者支持 distillation 说，后者支持复杂度说，两者预测的现象一致。要分开，需要固定复杂度分布重跑合成（例如约束 GPT-5 也产出同样比例的 high-level 工具），或用同一 constructor 产出高/低两套复杂度工具做对照，论文都没有做。

**统计处理缺位。** 全文单次运行、温度 0，没有种子、方差或置信区间。多个头条 delta 落在 0.2 到 2.5pp 区间，而 Reddit 子集只有 106 个任务，2pp 相当于两道题。GPT-5-mini 在 WALT 上的 ↓0.2 被写进"收益微弱或混合"的论证链条，但这个数字与噪声不可区分。跨模型的 sign pattern 整体一致性提供了一些间接支持，单格数字不宜单独引用。

**隐性税只算了在线的一半。** 论文承认工具合成本身开销不小，却没有给出任何合成阶段的 token 或时间数字。对于一个以成本为论点的章节，离线成本恰恰是更大的一半，尤其在"用 GPT-5 合成工具"被列为推荐做法的前提下。

**skill 对照同时改了两件事。** 从 Python 函数换成自然语言描述，既改变了表示形式，也取消了执行保证。GPT-5 的收益可能来自白盒可检视，也可能来自不再被错误的选择器绑死。要分开，可以给 agent 同时提供工具与其 skill 描述。此外这个结论建立在两个站点、两个模型上，GPT-5-nano 在 CMS 的 skill 成绩（9.3）低于其无工具基线（9.9），说明这条路径对弱模型是净损。

**数据记账有小的不一致。** Table 6 的任务总数在三套框架间不等：WALT 788、SkillWeaver 761、Hybrid-Agent 764，而 §3 声明的单站点任务总数是 764。Figure 1 与 Figure 2 隐含的 Hybrid-Agent 工具总数分别是 1946 与 1927，Table 1 的每站点 437 乘以五个站点则是 2185。这些差异不改变结论方向，但削弱了"三套框架跑在完全相同任务子集上"这一对照前提的可信度。

**评测面限于沙盒。** WEBARENA 与 VISUALWEBARENA 都是 DOM 稳定的镜像站点。合成工具最容易失效的场景是真实站点改版导致选择器漂移，论文引用的 SkillWeaver 原文本身就报告过真实网站结果，本文没有跟进。这意味着这里测到的"隐性税"很可能是下界。

**对领域的意义。** 把 tool library 当作 harness 的一个组件而非纯粹的能力增量来定价，是这篇文章最可迁移的一点：它的价值取决于写工具的模型与用工具的模型之间的能力差，而它的成本随库规模单调上升。这个结构同样适用于 skill library、memory 与任何形式的经验外置，不限于 web。

## Mind Map

```mermaid
mindmap
  root((ToolIllusion))
    Problem
      先前结论基于单一 tool source 与同家族 backbone
      SkillWeaver 与 WALT 结论互相矛盾
      工具是否一致有益 未被系统检验
    Method
      三 framework
        WALT 8 tools per site
        SkillWeaver 88 tools per site
        Hybrid-Agent 437 APIs per site
      五 backbone 跨三家族
      两 benchmark WebArena 与 VisualWebArena
      双向 scaling
        固定 developer 扫 user
        固定 user 扫 constructor
      对照
        tool 转 semantic skill
        视觉消融与反向注入
      未对齐项
        观测格式不同
        step 与 token 预算沿用各仓库默认
    Results
      人工 API 一致有益 最高 plus 19.6pp
      合成工具仅在 user 弱于 developer 时有效
      GPT-5 用 WALT 工具 52.9 降至 50.9
      SkillWeaver 62 percent high 复杂度 79 percent 零调用
      组合性决定上限 Hybrid-Agent ≥2 tools 52 percent 任务 41.2 percent
      隐性税 token 10.5M 升 33.9M 步数 7.1 升 8.3
      skill 利强模型 45.1 高于 base 43.4 损弱模型
      视觉仍有用 工具缩小视觉缺口
