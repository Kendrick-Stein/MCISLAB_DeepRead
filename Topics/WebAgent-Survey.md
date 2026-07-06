---
title: "Web Agent 研究综述"
tags: [web-agent, survey, gui-agent, deep-research, browser-agent]
date_updated: "2026-07-06"
year_range: 2022-2026
papers_analyzed: 39
keywords: [web agent, web navigation, browser agent, webarena, mind2web, deep research, information seeking, web environment, browsecomp, visual web agent]
domain_map: GUI-Agent
---

## Overview

Web Agent 是一类以 LLM/VLM 为大脑、在**浏览器/网页环境**中根据自然语言指令自主完成任务的 agent。它是 GUI/Computer-Use Agent 家族里**最早成形、也最先规模化**的分支：网页是标准化（HTML/DOM/AXTree）、可无限获取、且承载了电商、办公、政务、检索等绝大多数真实数字工作流，因此 web 天然成为 agent 落地的第一战场。本综述聚焦 **web 模态特有** 的问题，与已有的 [[Topics/ComputerUseAgents-Survey]]（desktop/OS 侧）、[[Topics/GUIAgent-Survey]]（宽领域）、[[Topics/GUI-Environment-Survey]]（环境基建）、[[Topics/RealWorldGUIAgent-Reliability-Survey]]（可靠性）互补——后四者不覆盖 web agent 独有的 **deep-research 信息检索支线** 与 **indirect/environmental prompt injection** 安全面。

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
- **World-model augmented**：用世界模型预测动作效果做 action correction（"World-Model-Augmented Web Agents", 2602.15384），与 [[Papers/2604-VeriGUI]] 的 action-effect 自验证同源。
- **Multi-agent / delegation**：[[Papers/2606-SearchSwarm]] 把 deep research 拆成 delegation 智能，多 agent 分工检索——长程信息任务的组织范式。

### 3. 训练范式（SFT / RL / verifier）

这是 Era 2 的主战场，核心是**摆脱闭源 API 依赖**：

- **轨迹合成 + SFT**：[[Papers/2412-AgentTrek]] 用 web tutorials 引导 replay 合成 agent 轨迹，解决 demonstration 稀缺。
- **Online curriculum RL**：[[Papers/2411-WebRL]]——self-evolving curriculum（失败即课程）+ ORM + KL 约束 + 置信度过滤回放，把 Llama-3.1-8B 在 WebArena-Lite 从 4.8%→42.4%，超 GPT-4-Turbo 17.6%。奠基工作。
- **大规模 visual web RL**：[[Papers/2606-WebGym]]（~292k realistic tasks + rubric binary reward + async rollout，OOD 26.2%→42.9%）、[[Papers/2606-AsyncWebRL]]（fully-async + 诊断 GRPO 的 `1/|τ|` step normalizer 会鼓励长失败轨迹，换成常数 `1/k` 后 42.9%→45.4%）、[[Papers/2508-ComputerRL]]（API-GUI 混合动作 + 千级并行 VM + Entropulse）。**共识：OOD 泛化来自任务分布 scaling + 可靠 verifier，而非新算法**。
- **Reward / verification**：从 [[Papers/2307-WebArena]] 的 functional correctness（程序化 state locator）→ [[Papers/2400-WebcanvasBenchmarkingWebAgents]] 的 keynode 中间态 → [[Papers/2606-WebGym]] 的 rubric-based LLM judge → WebRL 的 ORM。verifier 形态随可观测性退化，可靠性本身是研究对象。
- **Credit assignment / 偏好优化**：[[Papers/2509-TGPO]] 用树结构合并语义同状态消除偏好标签冲突 + process reward（子目标进度/冗余检测/动作验证），在 Online-Mind2Web 上更少冗余步——web 版细粒度信用分配。

### 4. Memory 与自我改进（非参数路线）

与 RL（参数化自演化）互补的是**非参数记忆/技能积累**：

- **Agent Workflow Memory (AWM)**（[[Papers/2409-AgentWorkflowMemory]]，ICML 2025）：从轨迹归纳可复用的自然语言 workflow，离线/在线均可，Mind2Web +24.6% / WebArena +51.1%（相对），且分布差距越大越领先——"what to do"。
- **SkillWeaver / Agent Skill Induction (ASI)**（[[Papers/2504-SkillWeaver]]）：归纳**可执行 Python skill**（可验证、可组合），补上"how to execute"这一端；SkillWeaver 显示强 agent 合成的 API 迁移给弱 agent 最高 +54.3%。
- **Context / reasoning memory**：[[Papers/2604-GenericAgent]]（contextual information density 最大化的 token-efficient 自演化）、ReasoningBank（推理记忆）、Hybrid Self-Evolving Structured Memory（2603.10291）。
- **成本视角**：预算约束研究（"Are Online Skill and Memory Modules Always Worth Their Tokens?", 2606.15017）提醒 memory/skill 模块并非总值回 token——效率是被低估的约束。

### 5. 环境与数据基础设施

"在什么上面训练/评测"是 web agent 的根本瓶颈（详见 [[Topics/GUI-Environment-Survey]]）：

- **Self-hosted 真实站点**：[[Papers/2307-WebArena]]（GitLab/Magento/Reddit/CMS Docker 化）——高真实、可复现，但站点数少。
- **Docker mirror 真实站点**：[[Papers/2600-WebHarbor]] 用 coding agent 把真实网站"dock"成本地 mirror（WebVoyager 15 站），保留视觉/账号/checkout 深功能 + 可 reset + human review 保真——真实与可控的折中。
- **合成环境**：[[Papers/2600-InfinitewebScalableWebEnvironment]] 用统一 spec + task-driven 后端 + 设计图引导前端，自动生成功能性网页 + 自动评估器，无限扩展（缓解 synthetic artifact 靠 review）。
- **大规模任务环境**：[[Papers/2606-WebGym]] 聚合 10 个 source（InSTA/PAE-WebVoyager/BrowseComp/Mind2Web-Live/GAIA-Web...）到 ~292k tasks / 127k 网站，OOD split。
- **统一 gym 生态**：[[Papers/2412-BrowserGymAgentLab]] 把 MiniWoB/WebArena/VisualWebArena/WorkArena/WebLINX/AssistantBench 统一成 gym API + AgentLab 实验框架——研究基础设施而非新 agent。

### 6. Deep Research / 信息检索支线

2025 年从"操作网页 GUI"分化出的独立支派，特征是**紧凑 action space（search + click + navigate）+ 长链推理**，目标是多跳检索、并行约束满足、跨源综合：

- **Tongyi WebAgent 家族**：WebWalker（benchmark）→ [[Papers/2505-WebDancer]]（ReAct 信息检索，browsing-data→SFT→RL 四阶段）→ [[Papers/2507-WebSailor]]（SailorFog-QA 高不确定性任务 + DUPO agentic RL，72B BrowseComp-en 12.0/zh 30.1/GAIA 55.4，超 Grok-3/Doubao）→ [[Papers/2508-WebWatcher]]（vision-language 多模态 deep research + BrowseComp-VL）→ [[Papers/2509-WebSailorV2]]（合成数据 + scalable RL，MoE，BrowseComp-en 35.3/zh 44.1/HLE 30.6，逼近闭源）→ WebResearcher/WebWeaver/AgentFold/WebLeaper（长上下文证据结构化）。
- **RL search agents**：Search-R1、DeepResearcher、Go-Browse。
- **Benchmark**：BrowseComp（OpenAI）、GAIA、[[Papers/2606-KBrowseComp]]（韩语，GPT-5.5 仅 45.67%，本土模型 0–10%，揭示非英语鸿沟）。
- 核心判断（[[Papers/2507-WebSailor]]）：**用高不确定性任务训练能得到向下兼容的推理能力**——难题上学的 fog-navigation 迁移到简单任务也涨。

### 7. 安全、隐私与治理（web 独有攻击面）

web agent 必然消费**不可信的第三方网页内容**，因此面临 GUI/desktop agent 没有的 **indirect / environmental prompt injection**：

- **攻击**：[[Papers/2605-WebTrap]]（parasitic goal fusion 中途劫持，真实站点 100% ASR）、[[Papers/2504-WASP]]（84 任务，realistic 威胁模型，86% 部分成功但完整攻击难——"security by incompetence"）、[[Papers/2409-EIA]]（环境注入窃隐私，Mind2Web PII 70%，ICLR 2025）、InjecAgent、SafeArena、VPI-Bench（视觉注入）。
- **防御/检测**：WebAgentGuard、WebSentinel、WAInjectBench（基于 WASP/EIA 场景的检测线）。
- **治理**：[[Papers/2500-PermissionManifestsWebAgents]] 提 `agent-permissions.json`（类 robots.txt 的机器可解析权限声明：resource/action 分层 + API-first）——在"全封禁"与"全放任"间建中间层。
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
| [[Papers/2504-WASP]] | 84 任务 | WebArena+注入 | attack success rate | 86% 部分 / 完整攻击低 | 现实威胁模型，动作劫持 |
| [[Papers/2409-EIA]] | Mind2Web+注入 | live 框架 | privacy leak ASR | PII 70% / 完整请求 16% | 环境注入窃隐私 (ICLR'25) |
| [[Papers/2412-BrowserGymAgentLab]] | 统一 6+ benchmark | gym 生态 | 各 benchmark | — | 研究基础设施 |

## Key Takeaways

1. **"进步幻觉"是本领域最重要的元结论**：旧 benchmark 因 shortcut 可解 + judge 不可靠系统性高估能力，真实 live 站点上多数 agent 仍在 SeeAct 水平、只有 Operator ~61%（[[Papers/2504-OnlineMind2Web]]）。任何新方法只报 WebVoyager/沙盒分数都应被质疑。**评测 realism 是被低估的核心瓶颈**。

2. **环境/数据稀缺 > 算法，是训练侧的第一瓶颈**：Era 2 的性能跃升主要来自"造更多真实任务 + 可靠 verifier + 高吞吐 rollout"（[[Papers/2411-WebRL]]/[[Papers/2606-WebGym]]/[[Papers/2600-WebHarbor]]/[[Papers/2600-InfinitewebScalableWebEnvironment]]），而非新 RL 算法。OOD 泛化来自任务分布 scaling。（建议加入 DomainMaps：GUI-Agent 的 web 训练环境已成独立子领域。）

3. **自我改进有两条正交路线**：参数化（RL 自演化课程，WebRL/ComputerRL）与非参数（NL workflow AWM / 可执行 skill ASI / 上下文记忆 GenericAgent）。二者可组合，且都把"失败轨迹"当一等训练资源——与 vault 的"造失败→学恢复"范式同源。

4. **Deep research 已从 GUI-operation 分化为独立范式**：紧凑 action space + 长推理，用高不确定性合成任务 + agentic RL 训练（[[Papers/2507-WebSailor]]）；但 BrowseComp 绝对分仍低（72B 仅 12% en），且与"操作真实网页 GUI"能力不互通——这是两种 web agent。

5. **可靠性瓶颈在 verify/recover 而非 grounding**：与 [[Topics/RealWorldGUIAgent-Reliability-Survey]] 的 web 侧证据一致——长程失败多来自"不知道自己错了"的空转，而非点不准。verifier 形态随可观测性退化（程序化→keynode→rubric LLM judge），judge 可靠性本身是开放问题。

6. **web agent 有 GUI/desktop 没有的安全面**：必然消费不可信第三方内容 → indirect/environmental prompt injection（WebTrap/WASP/EIA）。当前是"security by incompetence"，能力上升会放大风险；治理层（PermissionManifests）刚起步。

## Open Problems

1. **可信、低维护的真实评测**：live 站点会漂移、CAPTCHA/geo-block 干扰；WebJudge 仍有 ~15% 误判。如何做既真实又稳定可复现、judge 可信的评测？（Docker mirror vs live vs 合成的取舍未定论）
2. **长程可靠性：错误觉察 → 恢复**：真实多步任务的天花板由 verify/recover 决定；web 侧缺少像 [[Papers/2604-VeriGUI]] 那样系统的 action-effect 自验证 + 恢复训练。
3. **可扩展的可验证 reward（无 oracle）**：rubric-based LLM judge 依赖强模型且过严会伤 recall；如何在真实站点上低成本获得可靠 RL 监督？
4. **真正 OOD 网站泛化**：WebGym 已做 held-out 网站，但跨域（政务/金融/长尾 SaaS）泛化仍弱；grounding 跨分辨率/跨站鲁棒性未解（并入 [[Topics/GUIAgent-Survey]] 的 grounding robustness）。
5. **鲁棒的注入防御**：现有防御多为检测式、事后式；缺少能抵御 parasitic goal fusion（[[Papers/2605-WebTrap]]）这类隐蔽中途劫持的运行时机制。
6. **成本/token 效率**：长程 web 任务 context 爆炸、截图 IO 昂贵；memory/skill 模块的 token 性价比需按预算评估（2606.15017）。
7. **统一 GUI-operation 与 deep-research**：两支线目前割裂——既能操作真实网页界面、又能长程信息检索综合的通才 web agent 仍未出现（GAIA/AssistantBench 是早期交叉点）。
8. **非英语/多文化鸿沟**：[[Papers/2606-KBrowseComp]] 揭示 frontier 模型在韩语场景骤降、本土模型近乎失效——多语种 web agent 严重缺口。

## 调研日志
- **调研日期**: 2026-07-06（初版）；2026-07-06 增量（补 digest 15 篇遗留论文）
- **论文统计**: vault 已有相关 ~21 篇 + 首轮新 digest 3 篇（[[Papers/2411-WebRL]]、[[Papers/2504-OnlineMind2Web]]、[[Papers/2507-WebSailor]]）+ 增量 digest 15 篇 = 共 ~39 篇。
- **增量 digest 15 篇**: 综述——[[Papers/2503-WebAgentsSurvey]]、[[Papers/2506-DeepResearchAgents]]；记忆/技能——[[Papers/2409-AgentWorkflowMemory]]、[[Papers/2504-SkillWeaver]]；deep-research 家族——[[Papers/2505-WebDancer]]、[[Papers/2508-WebWatcher]]、[[Papers/2509-WebSailorV2]]；训练——[[Papers/2509-TGPO]]；安全——[[Papers/2504-WASP]]、[[Papers/2409-EIA]]；基础 benchmark——[[Papers/2401-VisualWebArena]]、[[Papers/2401-WebVoyager]]、[[Papers/2311-GAIA]]、[[Papers/2504-BrowseComp]]、[[Papers/2403-WorkArena]]。
- **外部检索**: WebSearch 6 次 + WebFetch 15 篇 arXiv abstract/HTML。
- **仍未 digest（供后续）**: "RL Foundations for Deep Research Systems" (2509.06733)、WebResearcher/WebWeaver/AgentFold/WebLeaper/WebShaper（Tongyi 家族其余）、InjecAgent/SafeArena/VPI-Bench（更多安全 benchmark）、WebLINX/AssistantBench（会话/长任务 benchmark）。
- **建议加入 DomainMaps**: "Web 训练环境 / 环境生成"作为 GUI-Agent domain 的独立子分支；"Deep Research 信息检索"作为 web agent 的独立范式节点。
