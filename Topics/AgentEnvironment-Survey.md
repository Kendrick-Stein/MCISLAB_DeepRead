---
title: "Agent Environment 综述——需求六轴、跨平台引擎与 agent-friendly 接口"
tags: [survey, gui-agent, environment-engineering, web-agent, computer-use, mobile-agent, agentic-RL, benchmark]
date_updated: "2026-07-21"
year_range: 2017-2026
papers_analyzed: 63
keywords: [agent environment, environment engine, web environment, gui environment, sandbox, testbed, snapshot, reset, parallel rollout, state fork, verifier, reward, task generation, rl infrastructure, agent-friendly, environment affordance, harness, deterministic replay]
domain_map: GUI-Agent
---

# Agent Environment 综述

> 本篇由三份 survey 于 2026-07-20 合并而成（Supervisor 指示同方向 survey 整合）：**WebEnvironment-Engine-Survey**（web 模态需求侧推导，2026-07-07，38 篇）提供主干；**GUI-Environment-Survey**（跨平台环境基建，2026-06-22，14 篇）并入 §3；**AgentFriendlyEnvironment-Survey**（AFE 概念与接口侧设计，2026-06-25，16 篇）并入 §4。原文见 git history。

## Overview

**一句话结论**：agent 环境工程十年演进的本质是把"面向人类的软件世界"重新改造成"面向程序的可编程状态转移系统"；其需求可归纳为六轴（初始化 / 评测 / 并行 / 回溯分支 / 任务供给 / 确定性与隔离），供给侧已在 web/mobile/desktop 三平台分别成熟，而**把这些能力作为 affordance 暴露给 agent 本身**（agent-friendly interface）仍是空白——这正是 primary direction（Agent-Facing Environment Runtime）的位置。

本综述按"需求 → 供给 → 接口"三层组织：

- **需求侧**（§1–2）：从 benchmark/训练环境演进史反推环境引擎该支持什么——六轴规格。
- **供给侧**（§3）：谁在造什么——跨平台（web/mobile/desktop/跨接口）环境基建格局。
- **接口侧**（§4）：环境能力暴露给谁、以什么形式——Agent-Friendly Environment 的定义、条件与协议。

**一个不可能三角贯穿始终**：realism（真实性）、controllability（可控性：reset/fork/verify）、scalability（并行成本）三者不可兼得。live web 有完美 realism 但 controllability≈0（[[Papers/2504-OnlineMind2Web]] 靠它揭穿"进步幻觉"，但 [[Papers/2502-InSTA]] 在它上面只敢做 read-only 任务）；Docker 自托管有完美 controllability 但 realism 有限且 scalability 差（WebArena 每容器 6.78GB / 启动近 1 分钟，[[Papers/2511-DreamGym]] 实测只能开 4 个并行 session 且需手动 sweep-reset）；合成环境 scalability 无限但 realism 存疑。2025–2026 的所有环境工作都在这个三角内找新的帕累托点：确定性副本（[[Papers/2504-REAL]]）、Docker mirror（[[Papers/2600-WebHarbor]]）、块级快照容器（[[Papers/2510-WebServ]]）、规范驱动合成（[[Papers/2600-InfinitewebScalableWebEnvironment]]）、browser-hosted functional simulation（[[Papers/2605-MobileGym]]）。

**为什么环境端成了瓶颈**：agent 侧的每一次范式升级，都会向环境端提出一批新需求，且环境需求**滞后于训练范式约一年才被显影**。prompting 时代（2023）只需要观察和终态打分；inference-time search 时代（2024）需要回溯；RL 时代（2024–2025）需要廉价 reset、大规模并行、可靠 reward；self-improving/大规模训练时代（2025–2026）需要任务自动生成和失败轨迹合成。每一代 benchmark 的"设计缺陷"，其实是上一代需求清单的化石。

**与其他 survey 的分工**：[[Topics/WebAgent-Survey]] 讲 web agent 方法侧演进；[[Topics/GUIAgent-Survey]] 讲 GUI agent 方法总览；[[Topics/AgentRuntimePrimitives-Survey]] 对 recovery/branching/parallelism 三原语做 related work 正面盘点（谁实现、暴露给谁）；[[Topics/RealWorldGUIAgent-Reliability-Survey]] 讲 agent 侧执行可靠性。本篇覆盖环境本体的需求、供给与接口设计。

## 1. 需求演进史：五幕（web 模态主线）

### 第一幕（2017–2022）：合成微环境——gym 语义免费，但任务太假

MiniWoB++（World of Bits 血统）和 WebShop 把网页做成合成小环境：reset 零成本、天然并行、reward 程序化——**RL 需要的所有引擎能力都免费满足**。教训是反向的：正因为环境是为 RL 设计的玩具，任务与真实 web 脱节，在其上饱和的方法迁移不到真实网站。这一幕确立了需求的"负样本"：**引擎能力不能以牺牲任务真实性为代价**。

### 第二幕（2023–2024）：自托管真实软件——可复现评测范式确立，训练需求尚未显影

[[Papers/2307-WebArena]] 是分水岭：Docker 化四个真实开源站点（GitLab/Magento/Reddit/CMS），bit-identical 镜像使 trajectory 可 byte-level 复现，**functional correctness**（程序化读取最终状态）取代 action-trace 表面比对。它一次性解决了"动态交互 + 真实环境 + 可复现 + 功能验证"，成为 de facto 模板（[[Papers/2401-VisualWebArena]]、[[Papers/2403-WorkArena]]、OSWorld、[[Papers/2409-WindowsAgentArena]] 都是该范式的移植）。[[Papers/2412-BrowserGymAgentLab]] 进一步把各 benchmark 统一成 gym API。

但 WebArena 是**为评测设计的**：每容器 ~6.78GB 存储、近 1 分钟冷启动、多任务共享同一 server 实例（跑完一批才能 reset，任务间状态互相污染）。这些在"跑一遍 812 个任务出分数"的场景下可以忍受，却为下一幕埋下伏笔。

### 第三幕（2024–2025）：live 评测运动——realism 最大化，暴露确定性与 judge 的双重危机

[[Papers/2401-WebVoyager]]（live 站点 + GPT-4V judge）、[[Papers/2400-WebcanvasBenchmarkingWebAgents]]（live + keynode 中间态）、[[Papers/2504-OnlineMind2Web]]（live + WebJudge，揭示"进步幻觉"：旧 benchmark 虚高，多数 agent 真实水平退回 SeeAct）把评测搬到真实互联网。收获是 realism 与"进步幻觉"的曝光；代价是**环境引擎能力归零**：不可 reset、不可复现（内容漂移、CAPTCHA、geo-block）、不可并行（速率限制）、评测只能依赖 LLM judge。

judge 的可靠性随即成为独立研究对象。[[Papers/2504-AgentRewardBench]] 给出系统测量：**12 个 LLM judge 无一 precision 超过 70%**（judge 判成功的轨迹 ~30% 实为失败），而 rule-based 评测 recall 仅 55.9%（WebArena 官方分比专家判定低 16.7pp）——**评测器在两个方向上同时不可靠**。verifier 可靠性与状态可观测性的正相关在 vault 证据链上完整成谱：程序化 verifier 94.1% 人类对齐（[[Papers/2605-OpenComputer]]）> 交互式 verifier agent 92.9%（[[Papers/2602-VAGEN]]，主动探测终态环境取证）> 视觉证据 judge 87.4%（[[Papers/2605-AndroidDaily]]）> WebJudge ~85% > 通用 judge ≤70%。[[Papers/2510-CUARewardBench]] 把 judge 审计扩展到 desktop（OSWorld 轨迹 + 专家标注）：最佳单模型 ORM precision 82.9%、PRM 仅 69.5%，且 CUA 专用训练反而损害 reward 判断能力——judge 不可靠在 web/desktop 双域成立。

### 第四幕（2024–2026）：RL 训练需求爆发——引擎从"能跑"到"吞吐优先"

[[Papers/2411-WebRL]] 证明 online RL 能让 8B 开源模型反超 GPT-4-Turbo 后，训练侧对环境的需求全面爆发，且每一项都有量化证据：

- **廉价 reset**：[[Papers/2509-AgentGymRL]] 不得不给 WebArena 加装 full-reset 接口（否则"状态不一致累积、污染学习信号"）和多 Chromium 子进程架构，还修复了 TextCraft/SciWorld 的内存泄漏才撑住大规模 RL——RL 训练把环境的工程缺陷全部逼了出来；[[Papers/2511-DreamGym]] 的第一手证词（Appendix A.3，已核实原文）："不存在可靠的 WebArena 开源 RL 基建，倾尽工程也只能开 4 个 AWS server / 4 个并行 session"，还要手动 sweep-reset 防跨任务污染、且官方评测函数存在已知误判——干脆放弃真实环境转向合成经验。
- **大规模并行**：[[Papers/2508-ComputerRL]] 用 Docker+gRPC 撑起千级 VM；[[Papers/2606-AsyncWebRL]] 全异步 rollout；[[Papers/2509-DARTGUI]] 解耦异步架构把环境利用率从 12.2% 提到 67.7%（5.5×）——**引擎工程效率的收益常常大于算法创新**。
- **可验证 reward**：[[Papers/2606-WebGym]]（~292k 任务 + rubric binary reward）与 [[Papers/2606-CUAGym]]（环境构建时同步生成 task/state/reward.py，产出 32K+ verified RLVR tuples）代表两条路线：前者用 judge 换覆盖面，后者把 reward 做进环境本体。
- **任务供给**：[[Papers/2502-InSTA]] 把任务生成推到 150k 个 live 站点（LLM proposer 89% 可验证 / safety filter 97% / judge 82.6%），$521 收集 2.2M 轨迹，1.7B 模型训到 56.9% 超过 235× 大的收集 policy。**共识：OOD 泛化来自任务分布 scaling，而非新算法**（WebGym/AsyncWebRL/InSTA 三方一致）。

[[Papers/2510-WebServ]] 是这一幕的需求集大成者，直接给出引擎规格书：Incus 容器 + ZFS block-level copy-on-write，启动 1.78s（Docker 8.96s）、每容器存储 28MiB（**Docker 6.78GB，240×**）、单机 200+ 并发，**运行中容器可快照/克隆/分支**；外加网络感知的确定性动作执行（拦截 XHR/fetch、等 idle window 才返回观察，消灭 SPA 异步竞态导致的 partially-observed 状态）。

### 第五幕（2025–2026，平行线）：环境不给，agent 自己造——需求的"负空间"

最能证明某个引擎能力有价值的证据，是**环境不提供时社区绕行的代价**。回溯（backtracking）是最典型的一轴：

1. [[Papers/2407-TreeSearchLMAgents]] 证明 inference-time tree search 收益巨大（VWA +39.7% 相对，弱模型 +119.7%，且随预算单调 scaling），但环境无快照，回溯只能"reset 环境 + 重放动作序列"——O(depth) 的昂贵模拟，还依赖确定性假设，只在沙盒可行。
2. [[Papers/2411-WebDreamer]] 明确指出 live 站点上 "resetting the environment or undoing action sequences is not feasible"，动作不可逆 + 搜索放大副作用 → 干脆把探索搬进 LLM 的参数化世界知识里做"想象模拟"。代价可量化：VWA 23.6% vs 真实搜索 26.4%（想象探索拿到真实探索 ~70% 的收益），且模拟深度 H>1 即退化。
3. [[Papers/2512-WebOperator]] 进一步指出 Tree Search/LATS/WebPilot 全都隐含假设动作可逆，提出 action-aware 安全回溯（动作可逆性四分类 + checkpoint URL 跳转 + 并行 tab speculative 回溯校验），WebArena 54.6% 大幅刷新 tree search 路线；其消融还发现 **naive tree search 反而掉分**（51.61% < 无搜索的 53.55%）——回溯的价值有前置条件（重放可行性校验）。需求因此细化为"**环境应显式标注动作可逆性 + 提供可靠 checkpoint**"：agent 侧启发式猜可逆性只有 ~37% 确认率，而这本是环境零成本掌握的元数据。
4. [[Papers/2511-DreamGym]] 则是训练侧的同构故事：真实环境并行开不起 → 推理式经验模型合成转移+reward 替代真实 rollout，WebArena 上零真实交互 GRPO 7.3→13.3；其 Theorem 1 还给出了替代路线的理论边界——合成训练的真实环境收益只取决于 **ε_R（reward 保真）+ ε_P（转移域一致）**，与 raw-state 复刻无关。但纯合成在 RL-ready 环境仍略低于真实 RL（S2R 混合才反超），说明合成是 warm-start 而非终局替代。

这条平行线的含义：**world model / 经验合成路线与环境引擎路线在竞争同一个需求**——要么环境提供廉价的真实状态分支，要么模型自己想象。二者的相对成本决定路线选择（详见 Takeaway 3）。三原语（recovery/branching/parallelism）由谁实现、暴露给谁的完整盘点已独立成 [[Topics/AgentRuntimePrimitives-Survey]]。

## 2. 需求轴分解：六轴规格

### 轴 1：初始化（init）——不止"能 reset"，而是"可编程的状态注入"

直觉里的"方便初始化"在论文中分化为三个层级，逐级变强：

| 层级 | 需求 | 实证 |
|:--|:--|:--|
| L1 冷启动速度 | 秒级创建/销毁实例 | [[Papers/2510-WebServ]] 1.78s vs Docker 8.96s；[[Papers/2605-MobileGym]] ~3s vs emulator ~78s |
| L2 状态重置 | 任务间快速回到已知初态、互不污染 | [[Papers/2600-WebHarbor]] SQLite sub-second reset + `/reset/<site>` control plane + seed db md5 校验；AgentGym-RL 给 WebArena 补 full-reset |
| L3 可编程注入 | 任意指定初始状态：数据 seed、边角场景、错误注入 | [[Papers/2504-REAL]] `/config` URL 参数（延迟/错误模式/价格乘数/位置预设）；[[Papers/2606-CUAGym]] state.py 程序化布置初态；OSWorld initial state setup script |

L3 是质变：只有可编程注入才支撑 (a) 边角场景评测（缺货、支付失败——生产网站永远测不到）、(b) 课程学习（把 agent 放到任务中段状态）、(c) 失败恢复训练数据合成（[[Papers/2605-GUIRobustEval]] 用可控 error depth 0/1/3/5 布置"已走错 N 步"的初态，合成 80 万恢复样本——**init 能力直接变成训练数据生成器**）。

### 轴 2：评测（verify/reward）——verifier 可靠性 ∝ 状态可观测性，评测与 reward 是同一问题

演进线：functional state check（[[Papers/2307-WebArena]]，需环境暴露后端状态）→ keynode 中间态（[[Papers/2400-WebcanvasBenchmarkingWebAgents]]，live 下的妥协）→ LLM judge（[[Papers/2401-WebVoyager]]/[[Papers/2504-OnlineMind2Web]]）→ judge 的系统性审计（[[Papers/2504-AgentRewardBench]]：precision ≤70%）→ **回摆向程序化**（[[Papers/2605-OpenComputer]] 94.1%；[[Papers/2504-REAL]] localStorage state-diff 断言；[[Papers/2606-CUAGym]] reward.py 与环境共生成）。

三个要点：

1. **verifier 形态由状态可观测性决定，不由 judge 聪明程度决定**。环境能暴露多少 hidden state，决定了评测的可靠性上限——把 verification 做成环境构建的组织原则（OpenComputer 的立场）而非事后脚本，是 2025–2026 的共识转向。
2. **评测与 RL reward 是同一个基础设施**（RLVR 视角）。AgentRewardBench 的 ~30% judge 假阳性会直接变成训练标签噪声（InSTA judge 82.6% 意味着 17% 噪声进入 SFT）；[[Papers/2606-ENVS]] 反过来用环境原生 oracle 过滤分支搜索轨迹当 SFT 监督——**环境 verifier 的每一点可靠性提升同时惠及评测与训练**。
3. **双向失败要求混合设计**：rule-based 低 recall（写死断言拒绝合法替代解）+ LLM judge 低 precision（看不见 hidden state）→ 程序化断言管 state-changing、rubric judge 管 information-seeking 的混合模式正在成型（REAL 已是这个结构；[[Ideas/HybridVerifier-GUIRuntime]] 的空间被证据确认）。另有反直觉发现：给 judge 的观察 screenshot-only 优于 screenshot+AXTree——**verifier 的观察也要做信息设计**。judge 本身还可特化小型化：[[Papers/2606-OpenWebRL]] 蒸馏的 8B judge（89.8% acc）超过 GPT-4o judge（85.6%）且评判成本近零——verifier 不必绑定 frontier 模型。

4. **2026 上半年的四条新路线按状态锚定深度排成谱系，锚定越浅 hacking 面越大**。[[Papers/2602-VAGEN]] 给出这条路线分化的第一性依据——验证不对称性：同一 Claude-Sonnet-4.5 在 OSWorld 上求解 55.9%（28.5 步）、验证 83.1%（17.4 步），验证比求解便宜得多，verifier 也应 agent 化。

| 路线 | 状态锚定 | 可靠性 | 代价 |
|:--|:--|:--|:--|
| 交互式 verifier agent（[[Papers/2602-VAGEN]]） | 最深：shell/python/computer-use 主动探测轨迹终态环境 | 92.9% acc（人评 GT）；弱 actor 下 precision 88.5%（passive judge 崩至 ~75%）；免手写脚本 | 须与轨迹终态环境在线耦合（离线轨迹不可用），17.4 步/条；read-only 仅 prompt 级软约束 |
| 加权 subtask 分解 + hidden verifier（[[Papers/2607-LongHorizonTerminalBench]]） | 深：hidden stress cases 程序化判分，gold solution 须拿满 1.0（相当于验证 grader 本身） | dense reward 把 62.8% 落在 partial 区间的 run 从零分中区分出来 | subtask 分解与权重人工设计，规模化到数百题存疑 |
| 一致性 ensemble + 弃权（[[Papers/2510-CUARewardBench]] UPE） | 浅：被动看截图序列 | ORM precision 89.8% / NPV 93.3% | recall 56.8%——用覆盖率换可靠性；未经 RL 闭环验证 |
| milestone dense reward（[[Papers/2602-ADMIRE]]） | 最浅：agent 自述 action description 与 milestone 文本 SBERT 匹配 | AndroidWorld 7B 44.0%（milestone 内容锚定环境 validator 判定成功的轨迹） | per-step 判定是 self-reported 文本，hacking 面从 judge 侧移到 policy 输出侧 |

谱系印证要点 1：交互式验证是目前唯一同时保住 precision 与 recall 的路线（UPE 弃权伤 recall，ADMIRE 判定不锚定状态），且它把"状态可观测性"从**环境预先暴露**改为 **verifier 按需获取**——与 AFE `verify()` affordance 是同一问题的两侧。

### 轴 3：并行（parallel）——瓶颈在 per-instance 成本与异步解耦，不在机器数

数字线索：4 个 session（[[Papers/2511-DreamGym]] 在 WebArena 上的极限）→ 256 并行/单机（MobileGym，~400MB/实例）→ 200+/单机（WebServ，28MiB/实例）→ 千级 VM（ComputerRL，靠钱堆）。两个杠杆：

- **per-instance 成本**：6.78GB→28MiB 的 240× 差距来自存储架构（分层文件系统整文件复制 vs block-level CoW），不是调参能解决的——**引擎选型即命运**。
- **异步解耦**：GPU（训练）与 CPU/浏览器（rollout）速度失配，同步架构让环境利用率只有 12.2%（[[Papers/2509-DARTGUI]]）；解耦后 67.7%。[[Papers/2606-AsyncWebRL]] 还发现同步假设泄漏进算法（GRPO 的 1/|τ| 归一化在异步长轨迹下鼓励失败）——**引擎架构与算法设计耦合，不是纯工程问题**。

### 轴 4：回溯与分支（fork/rollback）——最被低估的一轴，用途已分化为四类

关键澄清：**回溯不是浏览器 go_back**（丢失 scroll offset、表单输入等页内状态，[[Papers/2407-TreeSearchLMAgents]] 明确弃用），而是**完整环境状态（前端 + 后端 + session）的快照与恢复**。实现谱系：reset+replay 模拟（Tree Search，O(depth) 且要求确定性）→ JSON state forking（[[Papers/2605-MobileGym]]，functional 仿真才可行）→ **运行中容器块级快照/克隆/分支**（[[Papers/2510-WebServ]]，O(1) 原生操作）→ 想象模拟替代（[[Papers/2411-WebDreamer]]，live 下唯一选择）。agent 侧模拟的最新集大成是 [[Papers/2512-WebOperator]]（checkpoint 跳转 + speculative 回溯 + 可逆性分类，全靠浏览器技巧），其 37% destructive 确认率与"动态站点上可能退化为顺序搜索"的自认，正是 agent 侧模拟的天花板刻度。训练侧同款绕行见 [[Papers/2505-BacktrackAgent]]：检测到错误固定回退一步、同页重写动作，仅因 Mobile3M 是预遍历页面图（回退免费、不可逆问题被环境设定绕开）才可行；其 actual vs simulated outcome page 消融（task success +5.65 vs +0.70）把"回溯收益以状态转移真实性为前提"落到数字上。

用途已分化为四类，对应不同的调用方：

| 用途 | 调用方 | 实证 |
|:--|:--|:--|
| 探索性搜索（tree search 剪枝坏分支） | agent/推理框架 | Tree Search +39.7%；对比 trajectory reranking 平台在 30% 证明"能回头"是关键差异 |
| RL group rollout（同 prefix 分支采样） | 训练框架 | MobileGym state forking 支撑 GRPO；WebServ sub-rollout sampling / top-k expansion |
| counterfactual 评测（同状态反复 what-if、确定性重试、公平对比 policy） | 评测框架 | WebServ deterministic retries；[[Papers/2606-ENVS]] 分支搜索+oracle 过滤 |
| 失败恢复数据合成（从错误状态分支造恢复轨迹） | 数据管线 | [[Papers/2605-GUIRobustEval]] RoTS fragility-driven 分支合成 80 万样本 |

**第五种用途的空白**——把 fork/rollback 作为 affordance 暴露给 agent 本身在任务执行中调用——已在 sandbox 域被 [[Papers/2604-Crab]] 打穿：eBPF 追踪 turn 级"净变化"跳过 75–87% 不必要检查点、把 C/R 重叠进 LLM 推理等待窗口（p50 0.1s），`sbx.rollback(ckpt)` 作为 agent 可调用工具实证四场景收益（proactive recovery 步数 -29% / speculative execution / spot 迁移 / RL 树分支 token -40~64%）。但 Crab 的域是 shell/FS+process（不含浏览器 session 与后端 DB），且只测效率未测 success 因果——web 全栈状态 + 因果验证仍无人做（见 Takeaway 6）。

### 轴 5：任务供给（task supply）——直觉之外，环境价值 = 可验证任务数 × 多样性

多篇工作把瓶颈明确归到任务而非环境本体：WebRL 用 self-evolving curriculum 造任务；[[Papers/2606-WebGym]] 聚合 10 个来源到 292k 任务并证明 OOD 泛化随任务分布 scaling；[[Papers/2502-InSTA]] 把供给推到 150k 站点、并证明 LLM 当 task proposer/safety filter/judge 都够用；**探索式合成家族**给出四种设计——[[Papers/2410-NNetNav]]（interaction-first + hindsight relabeling，对环境要求最低：无需 reset/verifier，靠"每 4 步语言可命名性剪枝"控成本）、[[Papers/2502-Explorer]]（四阶段流水线 94K 轨迹 / $0.28 每条）、[[Papers/2506-GoBrowse]]（网站=图的结构化探索 + prefixed sampling 让弱模型从中间态起步贡献数据——**reset 频率直接决定 URL 覆盖 183→260**，reset 成本第一次被量化为数据质量约束）、[[Papers/2412-PAE]]（proposer-agent-evaluator 闭环 RL，"提案/评判 ≪ 执行"的 VLM 能力不对称使弱模型可给强 agent 供任务与 reward）；共同软肋是 judge 噪声（8.6%–19%）与沙盒-live 迁移崩塌（Go-Browse 21.7%→OOD 5.33%，NNetNav WebArena 训→live 仅 9.5%）；[[Papers/2603-AgentSynth]] 补上长程难度可控一环：先顺序生成并执行逐步可验证的简单子任务，再把子任务链总结成 agent 不可见的高层任务（information asymmetry）——难度 = 子任务数（SOTA agent 从 Level 1 的 18% 掉到 Level 6 的 4%），组合式 hard-task 生成成功率 52% vs 直接生成 11%，~$0.60/轨迹，且 task factory 与 environment runtime 天然分层（前者供给目标分布，后者供给状态/fork/verify）；[[Papers/2600-InfinitewebScalableWebEnvironment]] 干脆连网站带任务带评估器一起合成；[[Papers/2606-CUAGym]] 的范式最彻底——**task/state/reward 三件套与环境同步生成**，任务天生可验证。

推论：环境引擎的接口设计必须把"任务"当一等公民（task = 初态注入 + 终态断言 + 难度元数据），而不是环境之外的 prompt 列表。任务供给与轴 1（init 注入初态）和轴 2（reward 断言）在接口上是同一件事的三面。

### 轴 6：确定性执行与安全隔离——评测噪声与评测污染的最后一公里

- **确定性执行**：flaky 不只来自内容漂移，更来自**动作-观察竞态**——SPA 异步加载下"等固定时长"拿到 partially-observed 状态（[[Papers/2510-WebServ]] 的网络感知 idle 同步是目前最干净的解法）。数据层确定性则靠静态化（REAL 三件套：数据固定 + 时间锁定 + localStorage 状态）。live 环境无法确定性化时的次优解是**容错层**：[[Papers/2606-OpenWebRL]] 用 K8s 沙盒隔离 + 分级超时重试 + 七类结构化失败归因 + 站点黑名单撑起 80–100 并发的 live online RL（4B 平均 68.4% 追平 Gemini CUA），但其失败分析显示 **51% 的失败仍在环境接入层**（bot 检测/封锁/网络）——容错层是给不可控环境补的"伪引擎"，天花板明确。
- **安全隔离**：三重动机——(a) 真实副作用（live 下不敢做 transactional 任务，InSTA 因此把任务分布系统性偏向 read-only，**这是 live 训练路线的结构性天花板**）；(b) 受控注入评测（[[Papers/2504-WASP]]/[[Papers/2409-EIA]] 的 prompt injection 攻击评测只能在沙盒里做）；(c) 对外部世界的责任（InSTA 的每站 1 任务/30 动作限速协议）。
- **治理接口萌芽**：InSTA 的 agents.txt（站长声明速率限制、可访问范围、**自建 playground 副本**）与 [[Papers/2512-PermissionManifestsWebAgents]] 的 agent-permissions.json 是同一趋势——**环境对 agent 的声明式接口标准**，可视为"环境引擎需求"的站长侧镜像。

## 3. 跨平台环境格局：mobile / desktop / 跨接口

web 之外，mobile/desktop 环境基建沿同样的需求轴演进，并贡献了几个 web 端还没有的样板。

### 3.1 环境合成（Environment Synthesis）

**代表论文**：[[2604-AgentWorld]] · [[2600-InfinitewebScalableWebEnvironment]] · [[2605-EnvFactory]]

| 方法 | 环境规模 | 核心创新 | 局限 |
|:-----|:---------|:---------|:-----|
| **AgentWorld** | 1,978 环境 / 19,822 工具 | MCP servers + deep-research agent 自动挖掘工具接口；programmatic 双轨合成可验证任务 | 工具接口质量依赖爬取来源 |
| **InfiniteWeb** | 多样化网页环境 | 统一规范 + 任务驱动测试开发 + 网站种子与参考设计图像 | 主要针对 web，跨平台泛化未验证 |
| **EnvFactory** | 85 环境 / 2,575 轨迹 | Search+Code+Test 三 agent 协作；Pydantic schema + 可执行代码 + 单元测试验证 | 覆盖 domain 有限（tool-use 为主） |

设计哲学对比：AgentWorld bottom-up（从真实 API 出发）、InfiniteWeb top-down（从任务需求出发）、EnvFactory 质量优先（可执行性验证前置）。**环境合成的质量瓶颈在验证而非生成**——EnvFactory 把可执行性验证前置，AgentWorld 缺显式验证，InfiniteWeb 功能正确性依赖人工审核；自动验证合成环境与真实环境的行为一致性是下一步（Open Problem 3 的合成侧）。

### 3.2 Mobile / Desktop RL 基建：functional modeling 与 verifier-first 的两个样板

- **[[Papers/2605-MobileGym]]（browser-hosted mobile 仿真）**：三层 JSON state model（world data / runtime state / OS runtime state）实现 state forking 支持 GRPO group rollout；AnswerSheet protocol（typed state submission + 类型特定匹配器）取代 LLM judge；**95.1% sim-to-real retention** 证明 functional modeling（交互保真）而非像素级渲染才是 GUI 仿真的关键指标；~400MB RAM / ~3s 冷启动 / 单机 256 并行（AndroidWorld emulator ~4.5GB / ~78s）。
- **[[Papers/2605-OpenComputer]]（verifier-centric desktop）**：为 33 个桌面应用构建 app-specific 程序化 state verifier（1000 任务），多通道验证（D-Bus、LibreOffice UNO、SQLite、accessibility tree、直接文件解析）覆盖 hidden state 的不同观察窗口；硬编码 verifier 与人类判断对齐 **94.1%**（LLM judge 79.2%）——verification 作为环境构建的组织原则而非事后补救。
- **[[Papers/2509-DARTGUI]]（解耦异步 RL 架构）**：环境利用率 12.2%→67.7%（5.5×），7B 模型 OSWorld 42.13% 超越 Claude-4-Sonnet（详见轴 3）。

### 3.3 跨接口协同评测（GUI+CLI+Code）

- **[[2606-WeaveBench]]**：114 任务 / 8 领域的 hybrid interface benchmark，P1-P3 任务准入标准（channel non-substitutability / long-horizon / cross-application state）；**trajectory-aware judge**（5 层 pipeline）发现 outcome-only grading 系统性高估 10-20pp；失败分析 35.2% 是 **alignment gap（reward hacking）**而非能力不足；interface ablation 显示 hybrid gain +31.6pp、单接口全面崩溃——**hybrid interface 是真实工作流的盲区**，"35% 的失败不是做不出来，而是用错误方式绕过验证"。
- **[[2605-WorkspaceBench]]**：388 任务 / 20,476 文件 / 74 格式（源自字节 Lark 真实场景），异构文件理解与 lineage tracing 是核心瓶颈，best agent 68.7% vs 人类 80.7%。

### 3.4 Harness 优化：环境-agent 之间的可优化层

- **[[2606-RHO]]（self-supervised harness optimization）**：DPP 选 difficulty-diversity coreset + self-validation/self-consistency + pairwise self-preference，**无需外部标注**优化 harness（tools/prompts/skills）配置，SWE-Bench Pro 59%→78%；ablation 显示 self-consistency（cross-trajectory 矛盾检测，−0.22）比 self-validation（−0.08）更关键。
- **Harness-1（stateful retrieval harness）**：harness 维护可恢复搜索状态（候选文档、证据链接、验证记录），policy 只做高层决策——状态外部化思路可类比迁移到 GUI 操作环境。
- **[[Papers/2607-HarnessHandbook]]（harness 可维护性）**：harness 是随 model/API/环境持续演化的代码资产，修改请求用行为描述而 repo 按文件组织——L1–L3 behavior→implementation 映射 + Behavior-Guided Progressive Disclosure 让 coding agent 修改 harness 时 localization F1 +5.0–18.8pp、planner token -8.6~12.7%；与 RHO 互补（RHO 优化 harness 配置，Handbook 让 harness 代码本身可导航可编辑）。
- **[[Papers/2508-ComputerRL]]（API-GUI 统一）**：agent 同时掌握程序化 API 调用减少 3× 步数，9B OSWorld 48.9% 超 o3——harness 层的动作通道扩展是关键杠杆。

Harness 优化说明：**agent-friendly 不等于只改观察空间，也要改动作空间和 harness state**——很多失败并非模型不知道目标，而是被迫用错误粒度的动作通道完成任务。

## 4. Agent-Friendly Environment：接口侧设计

§1–3 的能力全部服务于 trainer/evaluator/数据管线。接口侧的问题是：这些能力能否、应否以 affordance 形式暴露给 agent 本身？

### 4.1 定义与边界

> **Agent-Friendly Environment（AFE）** = 面向 autonomous agents 设计的 dual-interface environment：人类仍看到正常 UI/app/OS，agent 额外获得一组 task-agnostic、state-grounded、executable、recoverable、verifiable、safe、cost-efficient 的环境 affordances。一个环境是 agent-friendly 的，当且仅当它在**不泄露任务答案、不替 agent 完成目标**的前提下，向 agent 暴露任务无关但状态绑定的 affordances，使 agent 能更可靠地 observe、act、recover、verify、guard 和 learn。

先定义边界是为了避免两个 trivial 化方向：把使用说明写成更长 prompt（prompt engineering）；给 agent 手写 task-specific macro action（RPA shortcut）。真正的研究价值在于：**不泄露任务答案，只把环境中本来存在但对 agent 不可见、不可控、不可验证的部分结构化暴露出来**。friendly 与 cheating 的分界：可以告诉 agent"当前页面有哪些合法 action / 当前 cart 有哪些 item"，不能告诉"下一步该点哪个按钮"。

### 4.2 七条件与 AFE Protocol

| 条件 | 含义 | 关键实证 |
|:--|:--|:--|
| 1. State-grounded | 信息来自当前真实状态（DOM/app state/DB/文件系统），非静态说明 | OpenComputer multi-channel state |
| 2. Task-agnostic | 暴露合法 action/状态，不暴露 gold next action | —（friendly vs oracle 边界） |
| 3. Executable | affordance 对应可执行 action/可查询 API，非文本建议 | ComputerRL API-GUI（3× 步数） |
| 4. Recoverable / Forkable | checkpoint、rollback、branch、reset、state diff | MobileGym state forking；WebServ O(1) 分支 |
| 5. Verifiable | 程序化 verifier、partial credit、progress signal | OpenComputer 94.1% vs LLM judge 79.2% |
| 6. Safe & Permissioned | 权限边界、敏感动作 confirmation、untrusted data 隔离、audit log | ToolEmu / AgentDojo |
| 7. Cost-efficient | 低成本并行、快速冷启动、状态快照复用 | MobileGym 400MB/3s；WebServ 28MiB/1.78s |

统一协议抽象（把 web/mobile/desktop/tool-use 的共同问题从"怎么点屏幕"抽象到"如何操控一个可验证的状态转移系统"）：

```text
observe()  -> screenshot + text tree + semantic state + state diff + provenance
act()      -> primitive GUI action + semantic action + CLI/API/tool action
recover()  -> checkpoint / restore / branch / reset / undo
verify()   -> progress probes / partial credit / final checker / consistency check
map()      -> route graph / app graph / file graph / workflow graph
guard()    -> permission / sandbox / untrusted-data boundary / side-effect policy
trace()    -> trajectory log / state delta / action provenance / replay artifact
```

各平台的 affordance 来源应尽量取自通用结构而非手写 skill（避免 RPA 化）：Web 用 route/DOM roles/form schema/API endpoints；Mobile 用 accessibility tree/app state schema/intent graph（MobileGym 证明 browser-hosted functional model 可行）；Desktop 用 window tree/filesystem/automation API/config DB（OpenComputer 是起点）；Tool-use 用 typed tool schema/state DB/permission spec（τ²-Bench 的 dual-control 与 user simulator）。

### 4.3 相关工作六分类：AFE 的局部组件已分别存在

文献中尚无统一成熟的 "agent-friendly environment" 概念，但已有工作分别做出了它的局部组件：

| 类别 | 代表工作 | 贡献的 AFE 组件 | 缺什么 |
|:--|:--|:--|:--|
| Gym-like 统一接口 | [[2412-BrowserGymAgentLab]]、AgentGym、[[2601-WebGym]] | 统一 observation/action space，解决 interface fragmentation | 统一 ≠ 友好：无 rollback/world map/verifier/权限 |
| Realistic 可执行环境 | OSWorld、AndroidWorld、[[Papers/2409-WindowsAgentArena]]、WebArena 系 | 真实软件状态 + execution-based 评测 | human-facing env repurposed for agents，未为 agent 重新设计 runtime |
| Verifier-first / State-grounded | [[Papers/2605-MobileGym]]、[[Papers/2605-OpenComputer]]、MobileWorld | 状态可见、可比、可 fork、结果可验证——AFE 核心骨架 | 能力留在 evaluator/trainer 手里，未暴露给 agent |
| Harness / Hybrid interface | [[Papers/2508-ComputerRL]]、[[2606-WeaveBench]]、Harness-1、[[2606-RHO]] | 动作空间与 harness state 的外部化 | harness 配置优化 ≠ 环境状态 affordance |
| Agent-facing recovery runtime | [[Papers/2604-Crab]] | rollback 作为 agent 可自调工具（`sbx.rollback`），四场景端到端效率收益 | 域限 shell/FS+process（无浏览器/后端 DB）；只测效率，无 success 因果与 prompt-only 对照 |
| Safety / Sandbox | ToolEmu、AgentDojo、OS-Harm | permission、side-effect control、untrusted data 隔离 | 安全组件未与其余 affordance 集成 |
| Multi-actor / Shared world | τ²-Bench、MobileWorld | user simulator、dual-control、Dec-POMDP 建模 | 单 agent 独占假设之外的状态隔离/归因未解决 |

### 4.4 关键判断

1. **AFE 不是"更简单的环境"，而是"更好的接口"**——保留任务目标和真实状态转移，只移除非本质摩擦（状态不可见、动作粒度过低、错误不可恢复、结果不可验证）。类比人类的 IDE/undo/debugger/file diff：instrumentation 不等于泄露答案。
2. **跨平台共同抽象是 state transition，不是 pixel UI**（MobileGym 的 95.1% retention 泛化）——研究目标不是做三个互不相干的 simulator，而是一套跨平台 environment protocol。
3. **Verifier 是环境的一部分，不是评测脚本的尾巴**——AFE 最小闭环是 `state → affordance → action → transition → verifier → feedback`。
4. **收益必须以 failure-mode reduction 论证**（navigation drift / loop / hidden-state mismatch / false completion / wrong-turn recovery），并正面对比 prompt-only baseline（把 AFE 信息序列化进 prompt 但禁用 executable API/rollback/verifier）——否则无法排除 prompt engineering 解释。
5. **Least-disclosure affordance**（2026-06-25 增补）：[[Papers/2606-AgentCIBench]]（无 adversary 时 contextual disclosure leakage 67.9%）+ [[Papers/2606-MyPCBench]] + [[Papers/2606-BraveGuard]] 三角证据说明 agent-facing state 不是单向利好——`observe_state()` 必须按 task scope、recipient、data category 过滤，`trace()` 应记录 evidence provenance。**AFE 的核心不是暴露更多 state，而是暴露正确粒度、正确范围、可审计的 state**。

研究设想（Core Claim、C0–C7 消融、AFE-MiniSuite、指标体系）已独立成 [[Ideas/AgentFacing-WebRuntime]] 与 [[Reports/2026-06-23-AgentFriendlyEnvironment-Proposal]]，此处不重复。

## 5. Datasets & Benchmarks

### 5.1 Web 环境引擎能力矩阵

| 环境/Benchmark | 年代 | realism | init/reset | 确定性 | 并行成本 | fork/回溯 | verifier 类型 |
|:--|:--|:--|:--|:--|:--|:--|:--|
| MiniWoB++ / WebShop | 2017/22 | 合成，低 | 零成本 | 完全 | 极低 | 无需（短程） | 程序化 |
| Mind2Web (static) | 2023 | 真实站快照 | N/A（离线轨迹） | 完全 | N/A | 不可交互 | step 比对 |
| [[Papers/2307-WebArena]] | 2023 | 真实开源软件 | Docker 重启，慢（~1min/6.78GB） | bit-identical | 差（DreamGym 实测 4 并发） | 无（Tree Search 靠 reset+replay 模拟） | functional state check |
| [[Papers/2401-WebVoyager]] / [[Papers/2504-OnlineMind2Web]] | 2024/25 | live，最高 | 不可 reset | 无（漂移/CAPTCHA） | 受限速 | 不可行（动作不可逆） | GPT-4V judge / WebJudge ~85% |
| [[Papers/2400-WebcanvasBenchmarkingWebAgents]] | 2024 | live | 不可 reset | 弱 | 受限 | 不可行 | keynode 中间态 |
| [[Papers/2504-REAL]] | 2025 | 11 个现代 SPA 副本 | `/clear` 秒级 + `/config` 可编程注入 | 完全（数据静态化+时间锁定） | 低（Vercel 托管、CDP session 级隔离） | localStorage 可整存整取（未做成 API） | localStorage state-diff 断言 + rubric judge |
| [[Papers/2600-WebHarbor]] | 2026 | 15 站 Docker mirror（真实后端） | SQLite sub-second reset + control plane | seed db md5 可验 | 中 | 未提供 | 任务级 + human review 保真 |
| [[Papers/2600-InfinitewebScalableWebEnvironment]] | 2026 | 合成（规范驱动） | 生成即初始化 | 完全 | 低 | 未提供 | 自动生成评估器 |
| [[Papers/2502-InSTA]] | 2025 | live 150k 站 | 不可 reset | 无 | 受责任限速 | 不可行 | LLM judge 82.6%（conf=1 时 93.1%） |
| [[Papers/2606-WebGym]] | 2026 | 真实站点 ~292k 任务 | 部分 | 弱 | 异步 rollout | 无 | rubric binary judge |
| [[Papers/2606-CUAGym]] | 2026 | mock apps | task/state.py 程序化 | 完全 | 低 | 支持（环境侧合成用） | reward.py 共生成（RLVR） |
| [[Papers/2510-WebServ]] | 2025 | 自托管（OCI 兼容） | **1.78s clone，28MiB/实例** | 网络感知 idle 同步 | **200+/单机** | **运行中容器块级快照/分支** | 状态可查（未内置 verifier 库） |
| [[Papers/2412-BrowserGymAgentLab]] | 2024 | 聚合 6+ benchmark | 沿用各自机制 | 沿用 | 沿用 | 无 | 统一接口层 |

矩阵读法：**没有一行全绿**。最接近"理想引擎"的 WebServ 缺 verifier 库与视觉观察；verifier 最强的 CUAGym/OpenComputer realism 受限于 mock apps；realism 最高的 live 系全线丧失引擎能力。这正是 Open Problem 1。

### 5.2 跨平台环境/评测

| Benchmark | 环境类型 | 规模 | 关键数字 | 特点 |
|:----------|:---------|:-----|:---------|:-----|
| **OSWorld** | Desktop (Linux/Win/Mac) | 369 任务 | 早期 14.41% vs 人类 78.24% | 容器隔离 + functional correctness，desktop 事实标准 |
| **AndroidWorld** | Mobile (emulator) | 116 任务 | 80.2% (MobileRL-9B) | 移动端长程任务标准参照 |
| **AndroidLab** | Mobile (真机) | 138 任务 | 53.6% (MobileRL-9B) | 在线交互评测，真实设备 |
| **[[Papers/2605-MobileGym]]** | Mobile (browser-hosted) | 416 任务 / 28 apps | GRPO +12.8pp (sim) / +40.7pp (real)；95.1% retention | functional simulation + state forking + AnswerSheet |
| **[[Papers/2605-OpenComputer]]** | Desktop (verifiable) | 1,000 任务 / 33 应用 | verifier-human 对齐 94.1% | multi-channel 程序化 verifier |
| **[[2606-WeaveBench]]** | Desktop (hybrid) | 114 任务 / 8 领域 | 41.2% (Claude Opus 4.7 + Claude Code) | GUI+CLI+Code 协同，trajectory-aware judge |
| **[[2605-WorkspaceBench]]** | Desktop (文件生态) | 388 任务 / 20,476 文件 | 68.7% vs 人类 80.7% | 异构文件依赖 + lineage tracing |
| **[[Papers/2607-LongHorizonTerminalBench]]** | Terminal (Docker) | 46 任务 | Grok 4.5 最佳 28.3% @R≥0.95；9.8M tokens / 239 episodes / 88.9min per run | 加权 subtask dense reward + hidden stress verifier；gold solution 须拿满 1.0 |
| **[[2604-AgentWorld]]** | Multi-tool (合成) | 1,978 环境 / 19,822 工具 | 23 个 benchmark 提升 | MCP + research agent 环境合成 |
| **[[2605-EnvFactory]]** | Tool-use (合成) | 85 环境 / 2,575 轨迹 | BFCLv3 +15% | 三 agent 协作 + 验证前置 |
| **ClawEval** | Multi-benchmark | 6 benchmarks / 11+ models | 95.8% vs official | 标准化评测复现性 |

**Benchmark 设计演进趋势**：单接口 → 跨接口协同（WeaveBench）；结果评估 → 过程诊断（trajectory-aware judge、reward hacking 检测）；固定任务 → 合成扩展（InfiniteWeb/EnvFactory/AgentWorld）；定性描述 → 程序化验证（OpenComputer）；仿真 → 真实迁移量化（MobileGym 95.1% retention 是首个系统测量）。

## Key Takeaways

1. **环境需求六轴，四条直觉全部证实但需升级表述**：初始化 → "可编程状态注入"（L3 才是质变，且直接变成数据生成器）；评测 → "状态可观测性决定 verifier 可靠性上限，评测与 reward 是同一基建"；并行 → "per-instance 成本 + 异步解耦，引擎架构与 RL 算法耦合"；回溯 → "完整状态快照/分支，用途已分化四类且 agent-facing 暴露是空白"。另补两轴：**任务供给**（环境价值 = 可验证任务数×多样性，task/state/reward 应共生成）与**确定性执行+安全隔离**（动作-观察竞态是 flakiness 的机制性来源；live 不敢做 transactional 是结构性天花板）。

2. **环境引擎在重新发明 OS/数据库的核心抽象**。六轴需求逐条对应成熟系统概念：可编程 init = seed/fixture、状态隔离 = transaction isolation、快照/分支 = copy-on-write fork、确定性重试 = record-replay debugging、state-diff verify = assertion、任务注入 = test harness。WebServ 用 ZFS CoW、REAL 用 localStorage 单存储、MobileGym 用 JSON state——都是把 web 栈搬回"状态是一等对象"的系统设计。**这个类比有预测力**：OS/DB 领域已解决而 agent env 还没搬过来的能力（如 MVCC 式多 agent 并发隔离、WAL 式状态审计日志）就是下一波工作。

3. **环境能力与模型能力可以互相替代，竞争同一预算**。环境不支持回溯 → WebDreamer 用 LLM 想象模拟（拿到真实搜索 ~70% 收益）；环境并行开不起 → [[Papers/2511-DreamGym]] 合成经验。替代的理论边界由 DreamGym Theorem 1 给出：合成路线的收益上限受 ε_R（reward 保真）+ ε_P（转移域一致）约束——**当真实引擎的并行/reset 成本降到合成推理成本以下，或任务要求的转移保真超出 LLM 先验，天平倒向引擎**。反向推论：引擎每把一项能力做便宜一个数量级（如快照 240×），对应的 world-model 绕行路线就失去必要性。评估任何 world-model-for-web 工作时，都应问"如果环境原生支持这个操作，该方法还剩什么价值"。

4. **评测环境与训练环境的需求已分化，同一环境难以同时最优**。评测要 determinism、防泄漏、严 verifier、固定任务集；训练要吞吐、dense/partial reward、任务多样性、允许 progress probe。REAL（binary reward，自认不适合 RL）与 WebGym（rubric judge 换覆盖面）各自只占一端。一个修正：dense/partial reward 不再是训练侧专属——[[Papers/2607-LongHorizonTerminalBench]] 显示难度触顶时评测同样需要 partial credit（782 个 run 仅 6.4% 通过、62.8% 落在 partial 区间、near-miss 多于通过，二值判分使多数模型并列零分而失去区分度）。环境设计应显式区分 eval mode / train mode / debug mode（affordance 暴露程度逐级放宽）。

5. **需求滞后镜像可用于预测**：环境需求跟着 agent 训练范式走、滞后约一年。按此推，2026–2027 的下一波需求：(a) 多 agent 并发同环境的隔离与归因；(b) 跨 session 持久状态（agent 记忆与环境状态的一致性）；(c) 环境侧 counterfactual 监督规模化（ENVS/CUAGym/GUI-RobustEval 已萌芽——环境引擎从"评测器"变成"数据工厂"）；(d) agent-native 声明式接口标准化（agents.txt / permission manifests 收敛）。

6. **对 primary direction 最重要的空隙**：六轴能力目前几乎全部服务于 trainer/evaluator/数据管线，**web 域没有任何环境把 snapshot/fork/verify 作为原生 affordance 暴露给 agent 在任务执行中自主调用**（WebServ 的快照是训练框架 API；[[Papers/2512-WebOperator]] 的 agent 侧模拟 37% 启发式噪声恰恰量化了缺环境支持的代价）。REAL 的失败模式分析显示 agent 缺的正是状态验证与回溯。demand-side 证据链已齐（Tree Search +39.7% / REAL 失败分析），supply-side 已便宜（WebServ O(1) 快照），中间的 agent-facing 接口层就是 [[Ideas/AgentFacing-WebRuntime]] 的位置——sandbox 域先例（[[Papers/2604-Crab]]：agent 自调 rollback 已实现且有端到端效率收益）与系统社区入场（AgenticExplorationSystems）使时间窗口收窄，详见 [[Topics/AgentRuntimePrimitives-Survey]] Takeaway 4。

7. **Functional modeling 足够好，跨平台共同抽象是 state transition**：MobileGym 证明"交互保真度"而非"像素级渲染"是 GUI 仿真的关键指标（95.1% sim-to-real retention，成本比 emulator 低一个数量级）。Web 的 route/DOM/backend state、Mobile 的 app/OS runtime state、Desktop 的 file/process/app state 本质都是状态转移系统——跨平台 environment protocol 比三个互不相干的 simulator 更是正确目标。

8. **Verification 是环境构建的组织原则，verifier 是环境的一部分**：OpenComputer 94.1% vs LLM judge 79.2% 的差距说明"谁来判断成功"比"环境多逼真"更根本；AFE 最小闭环 `state → affordance → action → transition → verifier → feedback`。混合设计（程序化断言管 state-changing、rubric judge 管 information-seeking）正在成型。第三条路线已出现：[[Papers/2602-VAGEN]] 的交互式 verifier agent（92.9% acc，免手写脚本）证明状态可观测性也可由 verifier 主动获取而非环境预先暴露——代价是与环境实例在线耦合。

9. **Hybrid interface 与 harness 是被低估的杠杆**：WeaveBench interface ablation +31.6pp、35.2% 失败是 reward hacking 而非能力不足；RHO 无标注 harness 优化 +19pp；ComputerRL API-GUI 减 3× 步数。agent-friendly 不只改观察空间，动作空间与 harness state 同样关键。

10. **AFE 的收益论证标准**：必须以 failure-mode reduction 呈现并通过 prompt-only 强对照（信息同等序列化进 prompt、禁用 executable/recoverable/verifiable affordance）；且 affordance 暴露须遵循 least-disclosure（AgentCIBench 67.9% leakage 的警示）——暴露正确粒度、正确范围、可审计的 state，而非更多 state。

## Open Problems

1. **不可能三角的量化**：realism–controllability–scalability 的取舍全靠定性论证，缺一个 fidelity metric 量化"副本/mirror/合成环境相对 live 的行为一致性"（MobileGym 95.1% retention 是 mobile 端孤例；web 端 REAL/WebHarbor 都没给这个数字；哪些交互必须 pixel-level、哪些 functional model 即可，无系统分析）。
2. **fork 语义的边界**：块级快照能恢复容器栈，但恢复不了外部世界（发出的邮件、第三方 API 调用、支付）——动作可逆性需要显式建模（WebOperator 方向）；快照粒度（浏览器 tab / session / 全栈）与成本的权衡未系统研究。
3. **verifier 与环境合成的可扩展性死结**：程序化 verifier 可靠（94.1%）但每任务手写不 scale；LLM judge scale 但 precision ≤70%。[[Papers/2602-VAGEN]] 的交互式验证提供第三解（免脚本 92.9%），死结松动但未解开——每条 17.4 步的验证成本在 RL rollout 规模下未验证，且 verifier 须与轨迹终态环境在线耦合、离线轨迹不可用。CUAGym 的"环境生成时共生成 verifier"是最有希望的解，但只在 mock apps 验证过；同构问题在环境合成侧：EnvFactory 的前置验证在千级环境规模下不可扩展，合成环境与真实环境的行为一致性缺自动验证手段。
4. **live 环境的 transactional 缺口**：InSTA 式 live 训练永远做不了状态修改任务，副本/mirror 又覆盖不了长尾站点。agents.txt 的 playground 提案（站长自建副本）是唯一指向系统性解法的方向，但没有任何激励机制研究。
5. **多 agent 并发环境**：所有现有引擎假设单 agent 独占实例；多 agent 共享世界（协作/竞争/人机共控 τ²-Bench 式）的状态隔离、冲突检测、贡献归因在 web 端完全空白——并行基建已成熟使此问题更迫切。
6. **agent-facing 暴露的因果验证**：fork/verify 作为 agent 可调用 affordance 的因果收益无对照实验（[[Papers/2604-Crab]] 只测效率不测 success）——AFE-MiniSuite C0–C7 对照（见 [[Reports/2026-06-23-AgentFriendlyEnvironment-Proposal]]）要补的正是这一点。
7. **Allowed affordance boundary 的形式化**：哪些 affordance 允许（当前状态/合法动作列表/结构图/state diff/undo/task-agnostic progress probe）、哪些算 oracle（gold next action/gold trajectory/task-specific macro/complete flag）需要写成协议和测试，而非口头解释——这是 AFE 方向不滑向 trivial 的关键。
8. **真实环境漂移**：live web/real app 的广告、A/B test、登录、schema migration 使 AFE adapter 面临持续维护成本；合理路径是先在 self-hosted but realistic 环境证明因果，再逐步接入真实环境。
9. **长程任务的 reward hacking 检测**：WeaveBench 35.2% 失败是 reward hacking，trajectory-aware judge 有额外 compute cost；lightweight 检测机制（如 cross-channel state consistency check）与 "alignment for GUI agents" 方法论未建立。新增三个未测的 hacking 面：[[Papers/2602-ADMIRE]] 的 milestone 命中判定取自 policy 自述文本（policy 可学会"把描述写得像 milestone"）；[[Papers/2602-VAGEN]] 的 verifier 与 actor 共享动作空间（actor 理论上可伪造 verifier 会检查的表面证据）；[[Papers/2607-LongHorizonTerminalBench]] 实测 14 个 run 在 R≥0.75 即自判完成退出（false finish——agent 系统性高估完成度、吝于做最终验证）。

## 调研日志

### 2026-07-21 增量并入 8 篇（survey-refresh）
- **队列 10 篇，跳过 2 篇**：WebOperator（已于 2026-07-07 增量并入，笔记无未覆盖内容）；SpectraReward（T2I 图像生成 reward，与 agent 环境无关，keyword 误报）。
- **并入**：[[Papers/2602-VAGEN]] / [[Papers/2510-CUARewardBench]] / [[Papers/2602-ADMIRE]] / [[Papers/2607-LongHorizonTerminalBench]]（轴 2 新增要点 4"状态锚定谱系"表 + 第三幕谱系插入 92.9% 档 + Takeaway 4/8 + OP 3/9）；[[Papers/2604-Crab]]（轴 4 第五用途改写 + §4.3 新增 Agent-facing recovery runtime 行 + Takeaway 6 / OP6 wikilink 化）；[[Papers/2505-BacktrackAgent]]（轴 4 实现谱系，simulated outcome page 消融）；[[Papers/2603-AgentSynth]]（轴 5，information asymmetry 任务工厂）；[[Papers/2607-HarnessHandbook]]（§3.4，harness 代码可维护性）。
- **结论修订**：OP3 verifier 可扩展性由"死结"改为"松动但未解开"（VAGEN 第三解）；Takeaway 4 修正"dense reward 是训练侧专属"（LHTB 证明评测侧同样需要 partial credit）。
- **status**: success

### 2026-07-20 三 survey 合并（本篇成立）
- **动因**: Supervisor 指示同方向 survey 合并。GUI-Environment-Survey（14 篇）、AgentFriendlyEnvironment-Survey（16 篇）、WebEnvironment-Engine-Survey（38 篇）同属环境工程方向，论文重叠 ~13 篇（MobileGym/OpenComputer/DART-GUI/ComputerRL/WeaveBench/BrowserGym/WebGym/AsyncWebRL/OSWorld/WebArena/WindowsAgentArena/InfiniteWeb/AgentStudio）。
- **结构**: WebEnvironment-Engine 的五幕史+六轴规格为主干（§1–2）；GUI-Environment 的跨平台基建并入 §3；AFE 的定义/七条件/协议/六分类并入 §4；AFE 研究设想部分不再重复（指针 → [[Ideas/AgentFacing-WebRuntime]] / [[Reports/2026-06-23-AgentFriendlyEnvironment-Proposal]]）。
- **Takeaway 合并**: 原 6+6+6 → 10 条（verification-as-organizing-principle、engine-efficiency、state-transition-abstraction 三处跨文重复各归一条）。
- **Open Problems 合并**: 原 6+5+6 → 9 条（多 agent 并发、fidelity metric、验证可扩展性三处重复合并；AFE OP5 eval/train 分化升为 Takeaway 4）。
- **status**: success

### 原 WebEnvironment-Engine-Survey 日志（2026-07-07）
- 初版 + 同日两轮增量（DreamGym；WebOperator/AgentGymRL/OpenWebRL/任务合成家族四篇）。vault ~24 篇直接相关 + 新 digest 14 篇 = 38 篇深度分析；WebSearch 8 次。DreamGym Appendix A.3 三条证词核实原文；Theorem 1 注入 Takeaway 3。仍未 digest：WAC (2602.15384)、UI-Simulator (2510.14969)、AgentSynth (2506.14205)。
- 与 [[Topics/AgentRuntimePrimitives-Survey]] 的分工：该篇对三原语做 related work 正面盘点，本篇（现 §1–2）做需求侧推导。

### 原 AgentFriendlyEnvironment-Survey 日志（2026-06-23/25）
- 从 [[Reports/2026-06-23-AgentFriendlyWebRuntime]] 展开；摘要级调研 + 本地笔记综合（BrowserGym/AgentGym/OSWorld/AndroidWorld/WindowsAgentArena/MobileWorld/ToolEmu/AgentDojo/τ²-Bench 等外部增量检索）。
- 2026-06-25 增补 least-disclosure 原则（MyPCBench/AgentCIBench/BraveGuard 三角证据）。

### 原 GUI-Environment-Survey 日志（2026-06-22）
- vault 14 篇重点分析（MobileGym, WeaveBench, RHO, OpenComputer, EnvFactory, AgentWorld, InfiniteWeb, WorkspaceBench, WebArena, AgenticEnvEng Survey, AgentStudio, DART-GUI, Harness-1, OSWorld）。
- 未能获取：AgenticEnvEng Survey 全文（arXiv 404）、Harness-1 全文（仅 GitHub README）。
