---
title: "Web Agent 研究综述"
tags: [web-agent, survey, gui-agent, deep-research, browser-agent]
date_updated: "2026-07-21"
year_range: 2022-2026
papers_analyzed: 71
keywords: [web agent, web navigation, browser agent, webarena, mind2web, deep research, information seeking, web environment, browsecomp, visual web agent]
domain_map: GUI-Agent
---

## Overview

Web Agent 是一类以 LLM/VLM 为大脑、在**浏览器/网页环境**中根据自然语言指令自主完成任务的 agent。它是 GUI/Computer-Use Agent 家族里**最早成形、也最先规模化**的分支：网页是标准化（HTML/DOM/AXTree）、可无限获取、且承载了电商、办公、政务、检索等绝大多数真实数字工作流，因此 web 天然成为 agent 落地的第一战场。本综述聚焦 **web 模态特有** 的问题，与已有的 [[Topics/GUIAgent-Survey]]（方法总览，含 desktop/computer-use 架构谱系）、[[Topics/AgentEnvironment-Survey]]（环境基建）、[[Topics/RealWorldGUIAgent-Reliability-Survey]]（可靠性）互补——后三者不覆盖 web agent 独有的 **deep-research 信息检索支线** 与 **indirect/environmental prompt injection** 安全面。

**核心问题分三层**：(1) **感知**——如何观察网页（DOM 文本 / 截图像素 / Set-of-Marks 混合），如何把语言指令 ground 到可操作元素；(2) **决策**——如何在长程、多标签页、状态可变的网页上规划并执行动作序列，并在出错时觉察与恢复；(3) **学习与评测**——用什么环境/数据训练，用什么 benchmark 可信地衡量真实能力。

**领域已相当成熟但远未饱和**。存在多篇专门 survey（[[Papers/2503-WebAgentsSurvey]]、[[Papers/2506-DeepResearchAgents]]、"RL Foundations for Deep Research Systems" 2509.06733），产业界全线入局（OpenAI Operator/CUA、Claude Computer Use、Google Project Mariner/Gemini Computer Use、Amazon Nova Act、browser-use、Microsoft Copilot Studio Computer Use）。然而 2025 年的标志性发现是**"进步幻觉"**——[[Papers/2504-OnlineMind2Web]] 证明旧 benchmark（WebVoyager ~90%）在真实 live 站点上崩塌，多数 agent 退回 2024 年初 SeeAct 水平，只有 Operator 达 ~61%。这条证据把领域焦点从"刷分"重新拉回"真实可部署性"。

**技术演进可分四个时代**：
- **Era 0 — 基础设施奠基（2022–2023）**：WebShop、MiniWoB++ 的合成环境；Mind2Web 的真实站点静态轨迹；[[Papers/2307-WebArena]] 确立 self-hosted 真实站点 + functional correctness 评测范式（至今是 de facto 模板）。
- **Era 1 — Prompting agent（2023–2024）**：SeeAct、WebVoyager、Synapse、AutoWebGLM、VisualWebArena——用闭源大模型 + 提示工程 + ReAct 组合，暴露"闭源依赖 + 泛化脆弱"。
- **Era 2 — 训练/RL 范式（2024–2025）**：[[Papers/2411-WebRL]]（self-evolving curriculum RL 让 8B 反超 GPT-4-Turbo）、AWM/ASI（memory/skill 自演化）、[[Papers/2606-WebGym]]/[[Papers/2606-AsyncWebRL]]/[[Papers/2508-ComputerRL]]（大规模 visual web RL），把能力从"调 API"转向"训得动开源模型"。
- **Era 3 — Deep research 分化（2025–2026）**：BrowseComp/GAIA 驱动的长程信息检索支线独立成派，[[Papers/2507-WebSailor]] 家族（WebWalker→WebDancer→WebSailor→WebWatcher）用高不确定性任务 + agentic RL 逼近闭源 DeepResearch。

一个贯穿全领域的张力是 **realism vs. scalability / controllability**：真实 live 网页最真但会被 CAPTCHA/geo-block/内容漂移污染、不可 reset、不可并行 RL；沙盒/合成环境可控可 scale 但丢失真实交互深度。2025–2026 的环境工作（[[Papers/2600-WebHarbor]] Docker mirror、[[Papers/2600-InfinitewebScalableWebEnvironment]] 合成环境、[[Papers/2606-WebGym]] 大规模任务）本质都在这个 spectrum 上找平衡点。

## 技术路线

### 1. 观察空间与视觉 Grounding

Web agent 的第一个设计轴是**"给模型看什么"**：

- **DOM / Accessibility Tree（文本）**：[[Papers/2307-WebArena]] 确立 AXTree + element ID 作为文本 agent 的观察基线，被大量后续工作沿用。优点是结构化、token 高效、动作可用 element-id 精确定位；缺点是丢失视觉布局、对渲染型/canvas 页面失效。
- **Screenshot（像素）**：visual web agent（VisualWebArena、[[Papers/2606-WebGym]]）让 agent 看渲染后的截图、输出 coordinate-based 动作，更贴近人类感知，但 grounding 更难、reward verification 更难。
- **Set-of-Marks / 混合**：[[Papers/2412-BrowserGymAgentLab]] 统一暴露 screenshot + DOM + AXTree + bid（唯一 element id）+ bbox + SoM，让 agent 兼取文本结构与视觉信息——已成为工程主流。
- **视觉 grounding 专线**：UGround（[[Papers/2400-NavigatingDigitalWorldAs]]）、SeeClick（[[Papers/2400-SeeclickHarnessingGuiGrounding]]）把"语言→屏幕坐标"作为可迁移能力单独训练，是 pixel-only web agent 的关键使能件。代表判断：fine-tuned grounding 显著强于通用 VLM（与 [[Topics/GUIAgent-Survey]] 的 grounding 结论一致）。

### 2. Agent 架构与推理

- **ReAct 闭环**：thought→action→observation 迭代，是 web agent 事实标准骨架（Operator/CUA、WebVoyager、WebDancer 均用）。
- **Planning / 分层**：把长程任务分解为子目标，缓解多步一致性问题；"Why Do LLM Web Agents Fail? A Hierarchical Planning Perspective"（2603.14248）指出失败常源于规划层而非执行层。
- **Inference-time search / 回溯**：[[Papers/2407-TreeSearchLMAgents]] 首证 best-first search + GPT-4o value function 在真实 web benchmark 有效（VWA 18.9%→26.4%，弱模型相对收益 +119.7%，随搜索预算单调 scaling），但回溯只能靠"reset 环境 + 重放动作序列"在沙盒模拟；[[Papers/2512-WebOperator]] 把隐含的"动作可逆"假设显式化——动作四分类（safe/destructive/terminating/invalid）+ checkpoint URL 跳转 + speculative backtracking（并行 tab 对照 snapshot 校验重放），WebArena 54.6% 且首次让 tree search 可用于 live 站点；其消融显示 **naive 回溯反而有害**（51.6% < 53.6%），回溯价值有"可行性校验"前置条件。
- **Agent 侧回溯谱系**：控制权与恢复机制两轴展开——[[Papers/2410-ExACT]]（ICLR 2025）R-MCTS（contrastive reflection + multi-agent debate 状态评估）把 VWA 相对提升 6–30%，其 Exploratory Learning 把搜索树摊平成单轨迹微调，1/4 token 恢复 ~87% 搜索性能，首证**搜索行为可蒸馏进模型**、但内化的上限仍是外部搜索；[[Papers/2504-WebRollback]]（EACL 2026）把多步回退做成 agent 自主调用的一等动作（critique 每步判 continue/rollback），live 站点零样本 +3~6pp、卡死率 19%→7%，恢复靠 URL 重定向——只能还原 URL 可编码的状态；[[Papers/2510-BranchAndBrowse]] 用 subtask 局部树搜索 + nearest-URL 混合重放 + background reasoning 预扩展 + page 级 action memory 把 WebArena 提到 35.8%（tree search baseline 19.2%）且时间 −40.4%，但单浏览器 session 无并行分支。三者与 WebOperator 共享同一天花板：**agent 侧恢复无法还原后端/session 状态**。
- **World-model augmented**：[[Papers/2411-WebDreamer]]（TMLR 2025）因"live 站点上 reset/undo 不可行"把探索搬进 LLM 想象——NL state-delta 模拟 + MPC 单步 lookahead，达到 tree search 收益的 ~70%（VWA 23.6% vs 26.4%）且 wall-clock 快 4.4×，但模拟深度 H=1 封顶（LLM 模拟误差随步数复合）；派生 [[Papers/2602-WAC]] 把模拟移到执行前做 pre-execution action correction（VWA +1.8pp / Online-Mind2Web +1.3pp——量级小，价值在于确立 simulate-before-act 作为廉价风险过滤原语），与 [[Papers/2604-VeriGUI]] 的 action-effect 自验证同源。
- **Multi-agent / delegation**：[[Papers/2606-SearchSwarm]] 把 deep research 拆成 delegation 智能，多 agent 分工检索——长程信息任务的组织范式。适用边界由 [[Papers/2512-ScalingAgentSystems]]（260 配置 × 5 架构受控研究）给出：MAS 平均收益 −0.3%，收益取决于任务可分解性与验证瓶颈——web 导航（顺序状态演化强）是最难受益的域（BrowseComp-Plus 上 independent 并行 −35%、无协调并行错误放大 17.2×），单 agent 基线 >45% 后加 agent 几乎必然负收益。

### 3. 训练范式（SFT / RL / verifier）

这是 Era 2 的主战场，核心是**摆脱闭源 API 依赖**：

- **轨迹合成 + SFT**：[[Papers/2412-AgentTrek]] 用 web tutorials 引导 replay 合成 agent 轨迹，解决 demonstration 稀缺；探索式合成已成体系化家族（PAE/NNetNav/Explorer/Go-Browse/AgentSynth，见第 5 节任务供给表）。人工标注的规模极点是 [[Papers/2603-WebChain]]：31,725 条真实网站轨迹（428 站，13.5× Mind2Web）+ 截图/AXTree/坐标三层对齐，人工采集绕过合成管线过不去的反爬/登录墙；其 Dual Mid-Training 消融显示 **mid-training 初始化决定 RL ceiling**、grounding 向的推理正则化反伤长程 RL——但评测全部是离线 step matching，与在线端到端成功率的鸿沟未测。
- **Online curriculum RL**：[[Papers/2411-WebRL]]——self-evolving curriculum（失败即课程）+ ORM + KL 约束 + 置信度过滤回放，把 Llama-3.1-8B 在 WebArena-Lite 从 4.8%→42.4%，超 GPT-4-Turbo 17.6%。奠基工作。
- **统一多环境 RL 框架**：[[Papers/2509-AgentGymRL]] 三模块解耦（环境 HTTP server-client / agent / 训练）覆盖 WebArena 等五类环境，ScalingInter-RL 交互 horizon 递增课程防"早期领先→训练中崩溃"，7B 五环境平均 +33.65 分；其 WebArena 基建改造清单（子进程多 Chromium 并行、episode 级 full-reset、内存泄漏治理）是"真实环境非 RL-ready"的又一第一手证据——与 [[Papers/2511-DreamGym]] 的 4 并发证词同源，但走了工程改造而非放弃真实环境的路线。
- **大规模 visual web RL**：[[Papers/2606-WebGym]]（~292k realistic tasks + rubric binary reward + async rollout，OOD 26.2%→42.9%）、[[Papers/2606-AsyncWebRL]]（fully-async + 诊断 GRPO 的 `1/|τ|` step normalizer 会鼓励长失败轨迹，换成常数 `1/k` 后 42.9%→45.4%）、[[Papers/2508-ComputerRL]]（API-GUI 混合动作 + 千级并行 VM + Entropulse）。**共识：OOD 泛化来自任务分布 scaling + 可靠 verifier，而非新算法**。
- **Live 站点 online RL**：[[Papers/2606-OpenWebRL]] 给出第一份完整开源配方——容错环境（K8s 沙盒隔离 + 分级超时重试 + 结构化失败归因 + 站点黑名单，80–100 并发）、412 条精选 SFT 热身（小而精保 policy plasticity：1.9K 轨迹反而 −2pp）+ MM-GRPO + rollout 长度课程，Qwen3-VL-4B 从 39.3% 提到 68.4%（WebVoyager/Online-Mind2Web/DeepShop 均值）追平 Gemini CUA；蒸馏 8B judge 89.8% acc 超 GPT-4o 且评判成本近零。代价清单同样清晰：**51% 失败在环境接入层**（bot 检测/封锁/网络）、无 reset/重放、依赖付费 stealth browser——live 路线的上限一半卡在环境接入。
- **合成经验替代真实 rollout**：[[Papers/2511-DreamGym]]（Meta）用 CoT 经验模型在抽象文本状态空间合成转移 + reward + reward-entropy 课程，零真实交互在 WebArena 超过真实环境 GRPO（7.3→13.3）、在 WebShop 追平 80K 真实交互，S2R 混合仅用 5K 真实数据反超；Theorem 1 说明合成环境只需 reward 保真 + 转移域一致，无需 raw-state 复刻。其 Appendix A.3 证词（WebArena 仅 4 并发 + 手动 reset + 官方评测误判）是"真实环境非 RL-ready"的第一手证据。[[Papers/2510-UISimulator]] 把 LLM 当通用 UI simulator（AXTree 状态 + LLM/规则混合转移函数，$0.02–0.05/轨迹），同等真实测试环境暴露下比 OS-Genesis 高 4×（WebArena），且**直接在真实环境合成经验反而更差**——合成环境的可控性（可覆盖失败分布）本身是训练价值来源。
- **搜索树 / 回退作为训练数据工厂**：[[Papers/2408-AgentQ]]（guided MCTS + 树上 Q 值差构造 step 偏好对 + off-policy DPO，OpenTable 18.6%→95.4%，失败轨迹变监督信号）、[[Papers/2410-ExACT]]（Exploratory Learning 把搜索树摊平成轨迹，模型内化探索-评估-回退行为）、[[Papers/2606-SRC]]（学生 K=3 步试探分支 + teacher 定位最早有害动作 + reset+replay 回退纠正 + quality-diversity archive，WebArena-Infinity +9.7pp；teacher 干预仅占样本 14.2% 却撬动全部增益——纠正点的信息密度远高于普通步）、[[Papers/2507-WebSynthesis]]（world-model MCTS 在虚拟 WebUI 合成轨迹，rollback 轨迹单独训练无效、须与成功轨迹组合才提供纠错信号）。共同前提是可回退/可重放的环境或模拟器；Agent Q 自白 MCTS 在 live 环境需大量 risky interaction、限制可安全部署的网站范围，是"分支探索需要沙盒/快照支持"的最直接证词。
- **Reward / verification**：从 [[Papers/2307-WebArena]] 的 functional correctness（程序化 state locator）→ [[Papers/2400-WebcanvasBenchmarkingWebAgents]] 的 keynode 中间态 → [[Papers/2606-WebGym]] 的 rubric-based LLM judge → WebRL 的 ORM。verifier 形态随可观测性退化，可靠性本身是研究对象。[[Papers/2504-AgentRewardBench]] 首次系统测量（1302 条专家标注轨迹）：12 个 LLM judge precision 无一超 70%，rule-based 评测 recall 仅 55.9%（官方分数系统性低估真实能力）——双向失败，评估器可靠性是 benchmark 打分与 RL reward 的公共上游瓶颈。
- **Credit assignment / 偏好优化**：[[Papers/2509-TGPO]] 用树结构合并语义同状态消除偏好标签冲突 + process reward（子目标进度/冗余检测/动作验证），在 Online-Mind2Web 上更少冗余步——web 版细粒度信用分配。
- **RL 收益的边界条件**：[[Papers/2607-GRPONullWebAgent]] 受控阴性结果——GRPO 在 SFT 已掌握的任务上无可信提升（McNemar p=0.50），中高学习率反而可信变差/崩溃（learning-rate 门控的 degrade/collapse 双机制），而在有 sampling headroom 的任务上同一 pipeline +22 分；[[Papers/2607-MAG]] 显示 base 成功率 <10% 时 plain GRPO 十次全部停摆（全失败 group 无 reward variance），须混入 expert 轨迹才能启动；加上 [[Papers/2603-WebChain]] 的"mid-training 决定 RL ceiling"，三者收敛为一个 pattern：**GRPO 主要是分布重塑而非能力注入，上下界都由 SFT/mid-training 初始化决定**。

### 4. Memory 与自我改进（非参数路线）

与 RL（参数化自演化）互补的是**非参数记忆/技能积累**：

- **Agent Workflow Memory (AWM)**（[[Papers/2409-AgentWorkflowMemory]]，ICML 2025）：从轨迹归纳可复用的自然语言 workflow，离线/在线均可，Mind2Web +24.6% / WebArena +51.1%（相对），且分布差距越大越领先——"what to do"。
- **SkillWeaver / Agent Skill Induction (ASI)**（[[Papers/2504-SkillWeaver]]）：归纳**可执行 Python skill**（可验证、可组合），补上"how to execute"这一端；SkillWeaver 显示强 agent 合成的 API 迁移给弱 agent 最高 +54.3%。
- **Context / reasoning memory**：[[Papers/2604-GenericAgent]]（contextual information density 最大化的 token-efficient 自演化）、ReasoningBank（推理记忆）、Hybrid Self-Evolving Structured Memory（2603.10291）。
- **程序化极点**：[[Papers/2602-ActionEngine]] 离线 Crawling Agent 构建应用级 state-machine graph（static/dynamic atom 区分控制状态爆炸，20-30 个 state 建模整个 Reddit 域），在线单次 LLM 调用合成 Python 程序确定性执行——WebArena Reddit 95%（AgentOccam 66%），成本 11.8×↓、LLM 调用 10.2→1.8 次/任务；把 AWM 的 workflow / ASI 的 skill 推进到"整个应用结构离线摊销 + O(1) 在线规划"的极点，vision fallback 失败后回写 memory 形成 self-healing。局限：per-application 构建、离线爬取成本未量化、单站点验证。
- **成本视角**：预算约束研究（"Are Online Skill and Memory Modules Always Worth Their Tokens?", 2606.15017）提醒 memory/skill 模块并非总值回 token——效率是被低估的约束。

### 5. 环境与数据基础设施

"在什么上面训练/评测"是 web agent 的根本瓶颈（详见 [[Topics/AgentEnvironment-Survey]]）：

- **Self-hosted 真实站点**：[[Papers/2307-WebArena]]（GitLab/Magento/Reddit/CMS Docker 化）——高真实、可复现，但站点数少。
- **Docker mirror 真实站点**：[[Papers/2600-WebHarbor]] 用 coding agent 把真实网站"dock"成本地 mirror（WebVoyager 15 站），保留视觉/账号/checkout 深功能 + 可 reset + human review 保真——真实与可控的折中。
- **确定性副本**：[[Papers/2504-REAL]] 用 React/Next.js 重建 11 个高频真实站点（Amazon/Gmail/Airbnb 等）的确定性副本——数据静态化 + 时间锁定 + 状态全存 localStorage，`/clear` 一键重置、`/config` 可编程初始化、`/finish` state-diff 断言；最强模型仅 41.07%（OpenAI CUA 7.14%）。代价是无真实后端，确定性用"砍掉动态性"换取。
- **合成环境**：[[Papers/2600-InfinitewebScalableWebEnvironment]] 用统一 spec + task-driven 后端 + 设计图引导前端，自动生成功能性网页 + 自动评估器，无限扩展（缓解 synthetic artifact 靠 review）。
- **Live 互联网做训练场**：[[Papers/2502-InSTA]] 用 LLM 三角色（task proposer 89% 可验证 / safety filter 97% / judge 82.6%）把任务供给从 ~200 站推到 150k 站点，$521 收集 2.2M 轨迹，Qwen3-1.7B 训后 56.9% 反超 235B 数据收集 policy；但 live 的天然代价是无 reset / 无重放 / 禁状态修改（任务系统性偏只读），judge 17% 错误率直接进入训练信号——其自提的 agents.txt / playground（站点自建仿真副本）提案正承认了这一缺口。
- **RL-ready 引擎原语**：[[Papers/2510-WebServ]] 用 Incus block-level copy-on-write 替换 Docker（启动 5×、存储 240×、单机 200+ 并发），实现**运行中容器的快照/克隆/分支**；其 Section 5.2 是目前最完整的环境引擎需求规格书（checkpoint / deterministic retry / sub-rollout sampling / counterfactual trial / cheap reset），但停留在基建验证——无端到端 RL 实验。
- **大规模任务环境**：[[Papers/2606-WebGym]] 聚合 10 个 source（InSTA/PAE-WebVoyager/BrowseComp/Mind2Web-Live/GAIA-Web...）到 ~292k tasks / 127k 网站，OOD split。
- **统一 gym 生态**：[[Papers/2412-BrowserGymAgentLab]] 把 MiniWoB/WebArena/VisualWebArena/WorkArena/WebLINX/AssistantBench 统一成 gym API + AgentLab 实验框架——研究基础设施而非新 agent。

**任务供给家族（数据工厂）**——"任务从哪来、轨迹怎么造"已从单点技巧发展为设计谱系：

| 工作 | 机制 | 规模 / 成本 | 下游结果 | 瓶颈表现 |
|:--|:--|:--|:--|:--|
| [[Papers/2412-PAE]] | proposer→agent→evaluator 闭环 + Filtered BC，无人工任务/reward | 每站 ~200 任务 | WebVoyager 33.0%（当时开源 SOTA），85 未见站 +5~7pp | evaluator 8.6% 误差进训练；失败轨迹全弃 |
| [[Papers/2410-NNetNav]] (ICML 2025) | interaction-first 探索 + hindsight 事后标注指令 + 层级剪枝 | 10k 演示 / 20 站 | 8B 超 zero-shot GPT-4（WA 16.3 / WV 35.2） | 沙盒→live 迁移仅 9.5% |
| [[Papers/2502-Explorer]] (ACL 2025 Findings) | proposer→refiner→summarizer→verifier 流水线，任务随探索细化 | 94,949 轨迹 / $0.28 条 | MM-Mind2Web step SR 53.2% | verifier 19% 标签噪声；流水线误差级联 |
| [[Papers/2506-GoBrowse]] | 网站=图的 BFS 发现 + prefixed sampling（从已发现中间态起步） | 9,504 轨迹 / $976 | WebArena 21.7% 超 NNetNav-7B | OOD 5.33% 崩塌；reset 频率制约 URL 覆盖 |
| [[Papers/2603-AgentSynth]] (ICLR 2026) | 简单可验证子任务链 + information asymmetry 总结成长程任务 | 6,000+ 任务 / ~$0.10 任务 | 难度梯度 L1 18%→L6 4%；hard 任务生成 52% vs 直接 11% | 质量控制仍依赖 LLM verifier |
| [[Papers/2502-InSTA]] | LLM 三角色（proposer/filter/judge）150k 站 | 2.2M 轨迹 / $521 | Qwen3-1.7B 反超 235B 数据收集 policy | judge 17% 错误率进训练信号 |

家族共同瓶颈有三：**judge/verifier 噪声（8.6–19%）直接进训练信号**、**安全协议（CAPTCHA/登录/支付即停）使任务分布系统性偏只读**、**站点绑定（沙盒合成数据在 live/OOD 上崩塌：NNetNav 9.5%、Go-Browse 5.33%）**。使能洞察来自 PAE：VLM 提任务与判结果远易于执行，故弱模型可为强 agent 供给任务与 reward——self-improving 训练环境由此可自举（后被 [[Papers/2606-OpenWebRL]] 的特化小 judge 超 GPT-4o 再次证实）。

### 6. Deep Research / 信息检索支线

2025 年从"操作网页 GUI"分化出的独立支派，特征是**紧凑 action space（search + click + navigate）+ 长链推理**，目标是多跳检索、并行约束满足、跨源综合：

- **Tongyi WebAgent 家族**：WebWalker（benchmark）→ [[Papers/2505-WebDancer]]（ReAct 信息检索，browsing-data→SFT→RL 四阶段）→ [[Papers/2507-WebSailor]]（SailorFog-QA 高不确定性任务 + DUPO agentic RL，72B BrowseComp-en 12.0/zh 30.1/GAIA 55.4，超 Grok-3/Doubao）→ [[Papers/2508-WebWatcher]]（vision-language 多模态 deep research + BrowseComp-VL）→ [[Papers/2509-WebSailorV2]]（合成数据 + scalable RL，MoE，BrowseComp-en 35.3/zh 44.1/HLE 30.6，逼近闭源）→ WebResearcher/WebWeaver/AgentFold/WebLeaper（长上下文证据结构化）。
- **RL search agents**：Search-R1、DeepResearcher。
- **宽检索（width scaling）支线**：与 depth（单 agent 长推理链）正交的维度，任务形态是多实体多属性汇总成表（WideSearch）。[[Papers/2602-WideSeekR1]] 把 lead-subagent 并行协调本身作为 MARL 训练对象（共享 4B 模型 + 上下文隔离 + 同 rollout 同组归一化 advantage + token/agent 双层重加权），WideSearch item F1 40.0% 追平 DeepSeek-R1-671B；关键证据是未训练的 multi-agent 随 subagent 数增加反而掉分——**组织能力需要训练，不是架构自带**。[[Papers/2607-SearchOS]] 走非参数路线：把检索进展从 prompt 历史外化为 relational schema + 共享状态四件套（Frontier Task / Evidence Graph / Coverage Map / Failure Memory）+ continuous scheduling + middleware 治理，WideSearch item F1 80.3——协调对象变成 transaction-like 共享状态。两者都在可分解、无状态副作用的宽检索域成立，与 [[Papers/2512-ScalingAgentSystems]] 的可分解性条件一致。
- **Benchmark**：BrowseComp（OpenAI）、GAIA、[[Papers/2606-KBrowseComp]]（韩语，GPT-5.5 仅 45.67%，本土模型 0–10%，揭示非英语鸿沟）。
- 核心判断（[[Papers/2507-WebSailor]]）：**用高不确定性任务训练能得到向下兼容的推理能力**——难题上学的 fog-navigation 迁移到简单任务也涨。

### 7. 安全、隐私与治理（web 独有攻击面）

web agent 必然消费**不可信的第三方网页内容**，因此面临 GUI/desktop agent 没有的 **indirect / environmental prompt injection**：

- **攻击**：[[Papers/2605-WebTrap]]（parasitic goal fusion 中途劫持，真实站点 100% ASR）、[[Papers/2504-WASP]]（84 任务，realistic 威胁模型，86% 部分成功但完整攻击难——"security by incompetence"）、[[Papers/2409-EIA]]（环境注入窃隐私，Mind2Web PII 70%，ICLR 2025）、InjecAgent、SafeArena、VPI-Bench（视觉注入）。
- **防御/检测**：WebAgentGuard、WebSentinel、WAInjectBench（基于 WASP/EIA 场景的检测线）。
- **安全评测方法论**：[[Papers/2607-VeraSafetyTesting]] 把攻击面从网页内容扩到工具返回通道（multi-channel 篡改 MCP 工具结果），并确立 **evidence-grounded verification**——安全违规以环境状态为准（state ⊳ tool ⊳ resp 优先级 + 非对称判定），意图/文本陈述不算违规；对 4 个 production agent 的 90%+ ASR 应读作"工具通道注入下普遍脆弱"的定性信号而非定量刻度（对象是 coding/tool agent，验证原理可直接迁移到 web agent 安全 benchmark）。
- **治理**：[[Papers/2512-PermissionManifestsWebAgents]] 提 `agent-permissions.json`（类 robots.txt 的机器可解析权限声明：resource/action 分层 + API-first）——在"全封禁"与"全放任"间建中间层；[[Papers/2502-InSTA]] Appendix D 的 agents.txt（速率限制 / 可访问页面 / 站点自建 playground 副本）是平行提案，两者可合并视为"环境对 agent 的声明式接口"。[[Papers/2607-AgentReadyWeb]] 提供网站侧改造的首个对照数据点：JSON-LD/aria-label/MCP 结构化改造把 browser-use agent 严格成功率 49.3%→89.3%、步数 −30%、token 最高 −40%——但 baseline 为作者自建（商品数据埋 JavaScript）有 strawman 风险、多项改动打包无 ablation，量级应打折扣读。
- 关键结论：当前安全主要是"security by incompetence"（靠 agent 无能而非鲁棒防御），一旦能力提升，注入风险会随之放大。

## Datasets & Benchmarks

| Benchmark | 规模 | 环境类型 | 评估指标 | SOTA / 关键数字 | 特点 |
|:--|:--|:--|:--|:--|:--|
| MiniWoB++ | ~100+ 模板 | 合成单页 | success rate | 近饱和 | 早期原子交互 |
| WebShop | 12k 商品 | 合成电商 | task score | — | 首个规模化电商 sim |
| Mind2Web (static) | 2350 任务/137 站 | 离线缓存 | element/step acc | — | 真实站点静态轨迹，禁探索 |
| [[Papers/2307-WebArena]] | 812 任务 | self-hosted 真实软件 | functional correctness | GPT-4 14.4% / 人类 78.2% | de facto 范式模板 |
| [[Papers/2401-VisualWebArena]] | 910 任务/3 站 | 沙盒 online | success rate | — | 多模态视觉推理，暴露 grounding gap |
| [[Papers/2401-WebVoyager]] | 643 任务/15 站 | live | GPT-4V-judge SR | 59.1%（后被证虚高） | 首个 live 截图端到端 + 自动评测 |
| Mind2Web-Live / [[Papers/2400-WebcanvasBenchmarkingWebAgents]] | 542 任务/2439 keynode | live | task SR / completion | best 23.1% SR | keynode 中间态评测 |
| [[Papers/2504-OnlineMind2Web]] | 300 任务/136 站 | live | WebJudge (~85% 人一致) | **Operator ~61%**，多数≈SeeAct | 反 shortcut，"进步幻觉"锚点 |
| [[Papers/2403-WorkArena]] / ++ | 33 / 682 任务 | ServiceNow 沙盒 | success rate | 开源<<闭源 | 企业知识工作，发布 BrowserGym |
| AssistantBench | 214 任务 | live | accuracy | 低 | 真实耗时任务 |
| [[Papers/2311-GAIA]] | 466 任务 | 工具+浏览 | accuracy | 人类 92% / GPT-4+plugins 15%；WebSailor-72B 55.4% | 通用助手/deep research 标尺 |
| [[Papers/2504-BrowseComp]] (en/zh) | 1266 题 | live | accuracy | WebSailor-72B 12.0/30.1；V2 35.3/44.1 | 答案难找易验证，高不确定性检索 |
| [[Papers/2606-KBrowseComp]] | 400 韩语 | live | accuracy | GPT-5.5 45.67% | 非英语鸿沟 |
| [[Papers/2606-WebGym]] | ~292k train / 1167 OOD | 真实站点(rubric) | rubric binary SR | 26.2%→42.9%（Qwen3-VL-8B RL） | 训练环境 scaling |
| [[Papers/2606-Ego2Web]] | egocentric video grounded | — | — | — | 用第一视角视频锚定任务 |
| [[Papers/2607-MAG]] | 581 任务/WebArena 6 live 站 | live replay | SR + GGS（执行 gated 的 guide 质量） | GPT-5.5 37.4% SR | "会做+会教"联合评测；grounding 偏好（SoM vs 坐标）模型特异 |
| [[Papers/2603-WebChain]] | 31,725 轨迹/318k 步/428 站 | 离线人工标注 | step matching（WCB-S/L） | 7B 训后公开基准 70.9→81.4 | 最大开源人工真实轨迹集，截图/AXTree/bbox 三层对齐 |
| [[Papers/2504-REAL]] | 112 任务/11 站 | 确定性 React 副本 | localStorage state-diff 断言 + rubric judge | Claude 3.7 Thinking 41.07% / CUA 7.14% | 确定性重放 + /config 可编程初始化 + impossible tasks |
| [[Papers/2504-AgentRewardBench]] | 1302 轨迹/351 任务 | 5 benchmark 轨迹集 | 专家标注测 judge P/R | LLM judge P ≤70% / rule-based R 55.9% | "评估器的评估"，双向失败测量 |
| [[Papers/2504-WASP]] | 84 任务 | WebArena+注入 | attack success rate | 86% 部分 / 完整攻击低 | 现实威胁模型，动作劫持 |
| [[Papers/2409-EIA]] | Mind2Web+注入 | live 框架 | privacy leak ASR | PII 70% / 完整请求 16% | 环境注入窃隐私 (ICLR'25) |
| [[Papers/2412-BrowserGymAgentLab]] | 统一 6+ benchmark | gym 生态 | 各 benchmark | — | 研究基础设施 |

## Key Takeaways

1. **"进步幻觉"是本领域最重要的元结论**：旧 benchmark 因 shortcut 可解 + judge 不可靠系统性高估能力，真实 live 站点上多数 agent 仍在 SeeAct 水平、只有 Operator ~61%（[[Papers/2504-OnlineMind2Web]]）。任何新方法只报 WebVoyager/沙盒分数都应被质疑。**评测 realism 是被低估的核心瓶颈**。

2. **环境/数据稀缺 > 算法，是训练侧的第一瓶颈**：Era 2 的性能跃升主要来自"造更多真实任务 + 可靠 verifier + 高吞吐 rollout"（[[Papers/2411-WebRL]]/[[Papers/2606-WebGym]]/[[Papers/2600-WebHarbor]]/[[Papers/2600-InfinitewebScalableWebEnvironment]]），而非新 RL 算法。OOD 泛化来自任务分布 scaling。任务供给已成体系化家族（第 5 节表），其三大共同瓶颈——judge 噪声进训练信号、只读偏置、站点绑定——把第一瓶颈进一步定位到**可验证性**；[[Papers/2606-OpenWebRL]] 补充另一半：数据侧质量清洗 > 数量（412 条精选 SFT 优于 1.9K），live RL 的上限一半卡在环境接入层（51% 失败为 bot 检测/封锁）。（建议加入 DomainMaps：GUI-Agent 的 web 训练环境已成独立子领域。）

3. **自我改进有两条正交路线**：参数化（RL 自演化课程，WebRL/ComputerRL）与非参数（NL workflow AWM / 可执行 skill ASI / 上下文记忆 GenericAgent / 应用级 state-machine memory [[Papers/2602-ActionEngine]]）。二者可组合，且都把"失败轨迹"当一等训练资源——与 vault 的"造失败→学恢复"范式同源。非参数路线的程序化极点（ActionEngine：结构离线摊销 + 单次调用合成程序，95% @ $0.06/任务）显示 reactive 逐步推理并非必需。

4. **Deep research 已从 GUI-operation 分化为独立范式**：紧凑 action space + 长推理，用高不确定性合成任务 + agentic RL 训练（[[Papers/2507-WebSailor]]）；但 BrowseComp 绝对分仍低（72B 仅 12% en），且与"操作真实网页 GUI"能力不互通——这是两种 web agent。

5. **可靠性瓶颈在 verify/recover 而非 grounding**：与 [[Topics/RealWorldGUIAgent-Reliability-Survey]] 的 web 侧证据一致——长程失败多来自"不知道自己错了"的空转，而非点不准。verifier 形态随可观测性退化（程序化→keynode→rubric LLM judge），judge 可靠性本身是开放问题——[[Papers/2504-AgentRewardBench]] 给出定量下界：LLM judge precision ≤70%（说成功的 ~30% 其实失败）、rule-based recall 55.9%（系统性漏判成功），且副作用检测近乎不可用（precision 7–14%）。

6. **web agent 有 GUI/desktop 没有的安全面**：必然消费不可信第三方内容 → indirect/environmental prompt injection（WebTrap/WASP/EIA）。当前是"security by incompetence"，能力上升会放大风险；治理层（PermissionManifests/agents.txt）刚起步。

7. **回溯/搜索的价值已被证实，其天花板由环境状态原语决定**：证据链——真实探索有大收益但依赖 reset+replay 模拟回溯（[[Papers/2407-TreeSearchLMAgents]] +39.7%）；live 站点不支持回溯，只能退化为想象模拟（[[Papers/2411-WebDreamer]]，收益 ~70% 且深度 H=1 封顶）、agent 侧投机回溯（[[Papers/2512-WebOperator]]，destructive 动作启发式确认率仅 37%）、agent 自主 rollback（[[Papers/2504-WebRollback]]，URL 重定向只能还原 URL 可编码状态）或混合重放（[[Papers/2510-BranchAndBrowse]]，单 session 无并行分支）；而动作可逆性、状态序列化恰是环境端零成本掌握的信息。引擎侧回应已出现（[[Papers/2510-WebServ]] O(1) 快照/分支），极端解是整个放弃真实环境（[[Papers/2511-DreamGym]] 合成经验）。两条新支线不改变结论：训练侧把搜索树/回退当数据工厂（[[Papers/2408-AgentQ]]/[[Papers/2606-SRC]]/[[Papers/2410-ExACT]]/[[Papers/2507-WebSynthesis]]）同样以可 reset/可重放为前提；内化路线（ExACT EL 恢复 ~87%、Agent Q 训后 search gap 持久存在）证明搜索行为可蒸馏但不能被完全替代。"环境原生 fork/rollback + 可逆性元数据"是这条证据链指向的共同缺口。

8. **RL 收益有明确边界条件，正结果报账需受控对照**：[[Papers/2607-GRPONullWebAgent]]（受控 null：GRPO 在已掌握任务上无可信提升，只在有 sampling headroom 时重塑分布）+ [[Papers/2607-MAG]]（base 成功率 <10% 时 plain GRPO 停摆，需 expert 轨迹注入启动）+ [[Papers/2603-WebChain]]（mid-training 初始化决定 RL ceiling）共同表明：**web agent RL 的上下界都由 SFT/mid-training 决定，GRPO 主要是分布重塑而非能力注入**。这与 Takeaway 2（收益来自任务/数据而非算法）互为印证，也意味着 RL 正结果应控制 headroom 并做配对统计，否则不可信。

9. **multi-agent 并行的收益取决于任务可分解性，web 导航是最难受益的域**：[[Papers/2512-ScalingAgentSystems]]（260 配置受控）测得 MAS 平均收益 −0.3%、无协调并行错误放大 17.2×、单 agent 基线 >45% 后加 agent 几乎必然负收益，web 导航因顺序状态演化强而属最难受益域；可分解、无副作用的宽检索是例外，且需把协调本身作为训练对象（[[Papers/2602-WideSeekR1]] 未训练时负 scaling、训练后 4B 追平 671B）或做成共享状态结构（[[Papers/2607-SearchOS]]）才能解锁。

## Open Problems

1. **可信、低维护的真实评测**：live 站点会漂移、CAPTCHA/geo-block 干扰；WebJudge 仍有 ~15% 误判。如何做既真实又稳定可复现、judge 可信的评测？（Docker mirror vs live vs 合成的取舍未定论）
2. **长程可靠性：错误觉察 → 恢复**：真实多步任务的天花板由 verify/recover 决定；web 侧缺少像 [[Papers/2604-VeriGUI]] 那样系统的 action-effect 自验证 + 恢复训练。
3. **可扩展的可验证 reward（无 oracle）**：rubric-based LLM judge 依赖强模型且过严会伤 recall；如何在真实站点上低成本获得可靠 RL 监督？进展信号：verifier 可特化小型化（[[Papers/2606-OpenWebRL]] 蒸馏 8B judge 89.8% 超 GPT-4o、成本近零），但 ~10% 噪声仍直接进梯度。
4. **真正 OOD 网站泛化**：WebGym 已做 held-out 网站，但跨域（政务/金融/长尾 SaaS）泛化仍弱；grounding 跨分辨率/跨站鲁棒性未解（并入 [[Topics/GUIAgent-Survey]] 的 grounding robustness）。
5. **鲁棒的注入防御**：现有防御多为检测式、事后式；缺少能抵御 parasitic goal fusion（[[Papers/2605-WebTrap]]）这类隐蔽中途劫持的运行时机制。
6. **成本/token 效率**：长程 web 任务 context 爆炸、截图 IO 昂贵；memory/skill 模块的 token 性价比需按预算评估（2606.15017）。
7. **统一 GUI-operation 与 deep-research**：两支线目前割裂——既能操作真实网页界面、又能长程信息检索综合的通才 web agent 仍未出现（GAIA/AssistantBench 是早期交叉点）。
8. **非英语/多文化鸿沟**：[[Papers/2606-KBrowseComp]] 揭示 frontier 模型在韩语场景骤降、本土模型近乎失效——多语种 web agent 严重缺口。
9. **状态修改型（transactional）任务的供给与验证**：live 合成管线的安全协议（CAPTCHA/登录/支付即停）使训练分布系统性偏只读（[[Papers/2502-Explorer]]/[[Papers/2502-InSTA]]/[[Papers/2410-NNetNav]] 同款约束），沙盒内修改型任务又受 reset 成本制约（[[Papers/2506-GoBrowse]] 的 reset 频率 ↔ 覆盖权衡）——写操作能力的训练数据是结构性缺口。

## 调研日志
- **调研日期**: 2026-07-06（初版）；2026-07-06 增量（补 digest 15 篇遗留论文）；2026-07-19 survey-refresh（并入 8 篇 07-07 记账批次：搜索/回溯 [[Papers/2407-TreeSearchLMAgents]]/[[Papers/2411-WebDreamer]]/[[Papers/2512-WebOperator]]，环境/引擎 [[Papers/2504-REAL]]/[[Papers/2502-InSTA]]/[[Papers/2510-WebServ]]，训练/评测 [[Papers/2511-DreamGym]]/[[Papers/2504-AgentRewardBench]]；新增 Key Takeaway 7"回溯价值与环境状态原语缺口"；另清账 15 篇 07-06 重复记账条目——初版构建当日已并入正文）；2026-07-21 survey-refresh（并入 24 篇：搜索/回溯与数据工厂 [[Papers/2410-ExACT]]/[[Papers/2408-AgentQ]]/[[Papers/2504-WebRollback]]/[[Papers/2510-BranchAndBrowse]]/[[Papers/2606-SRC]]/[[Papers/2507-WebSynthesis]]/[[Papers/2602-WAC]]；任务供给家族 [[Papers/2412-PAE]]/[[Papers/2410-NNetNav]]/[[Papers/2502-Explorer]]/[[Papers/2506-GoBrowse]]/[[Papers/2603-AgentSynth]]；训练 [[Papers/2606-OpenWebRL]]/[[Papers/2509-AgentGymRL]]/[[Papers/2510-UISimulator]]/[[Papers/2607-GRPONullWebAgent]]/[[Papers/2607-MAG]]/[[Papers/2603-WebChain]]；memory/架构 [[Papers/2602-ActionEngine]]；multi-agent/宽检索 [[Papers/2512-ScalingAgentSystems]]/[[Papers/2602-WideSeekR1]]/[[Papers/2607-SearchOS]]；安全/治理 [[Papers/2607-VeraSafetyTesting]]/[[Papers/2607-AgentReadyWeb]]。新增第 5 节任务供给家族表、Key Takeaways 8（RL 收益边界）/9（multi-agent 边界）、Open Problem 9（transactional 任务缺口）。跳过 2 篇：AgenticAISupervisor（非浏览器工具模拟 RL 平台预告，纯环境基建）、SearchGenBoundary（图像生成 knowledge boundary 主题））
- **论文统计**: vault 已有相关 ~21 篇 + 首轮新 digest 3 篇（[[Papers/2411-WebRL]]、[[Papers/2504-OnlineMind2Web]]、[[Papers/2507-WebSailor]]）+ 增量 digest 15 篇 = 共 ~39 篇。
- **增量 digest 15 篇**: 综述——[[Papers/2503-WebAgentsSurvey]]、[[Papers/2506-DeepResearchAgents]]；记忆/技能——[[Papers/2409-AgentWorkflowMemory]]、[[Papers/2504-SkillWeaver]]；deep-research 家族——[[Papers/2505-WebDancer]]、[[Papers/2508-WebWatcher]]、[[Papers/2509-WebSailorV2]]；训练——[[Papers/2509-TGPO]]；安全——[[Papers/2504-WASP]]、[[Papers/2409-EIA]]；基础 benchmark——[[Papers/2401-VisualWebArena]]、[[Papers/2401-WebVoyager]]、[[Papers/2311-GAIA]]、[[Papers/2504-BrowseComp]]、[[Papers/2403-WorkArena]]。
- **外部检索**: WebSearch 6 次 + WebFetch 15 篇 arXiv abstract/HTML。
- **仍未 digest（供后续）**: "RL Foundations for Deep Research Systems" (2509.06733)、WebResearcher/WebWeaver/AgentFold/WebLeaper/WebShaper（Tongyi 家族其余）、InjecAgent/SafeArena/VPI-Bench（更多安全 benchmark）、WebLINX/AssistantBench（会话/长任务 benchmark）。
- **建议加入 DomainMaps**: "Web 训练环境 / 环境生成"作为 GUI-Agent domain 的独立子分支；"Deep Research 信息检索"作为 web agent 的独立范式节点。
