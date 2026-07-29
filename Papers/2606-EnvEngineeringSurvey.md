---
title: "Agentic Environment Engineering for Large Language Models: A Survey of Environment Modeling, Synthesis, Evaluation, and Application"
authors: ["Jiachun Li", "Zhuoran Jin", "Tianyi Men", "Yupu Hao", "Kejian Zhu", "Lingshuai Wang", "Dongqi Huang", "Longxiang Wang", "Shengjia Hua", "Lu Wang", "Jinshan Gao", "Hongbang Yuan", "Ruilin Xu", "Kang Liu", "Jun Zhao"]
institute: ["Institute of Automation, Chinese Academy of Sciences"]
date_publish: "2026-06-10"
venue: "arXiv"
tags: [agentic-RL, LLM, world-model]
url: "https://arxiv.org/abs/2606.12191"
arxiv_id: "2606.12191"
doi: ""
cite_key: li2026agentic
code: ""
rating: "4"
content_scope: "full-text"
verification_status: "source-checked"
date_added: "2026-07-29"
---
## Summary

CASIA 团队的 agentic environment engineering anchor survey（63 页，582 篇文献）：把环境从"静态数据集/评测台"升格为一等工程对象，按全生命周期组织——modeling（八属性二分 × 八 domain）→ synthesis（symbolic 三段 + neural 三层）→ evaluation（correctness/diversity/complexity/fidelity 四维）→ application（agent 演化四路径 + 环境演化三范式的闭环 co-evolution）。核心判断：环境质量评估中只有 correctness 成熟，diversity/complexity/fidelity 均 under-researched；未来指向 Environment-as-a-Service、multi-agent environments 与 neural-symbolic integration。

## Problem & Motivation

作者的出发点是 data engineering → environment engineering 的范式迁移，用三个 shift 界定"环境"区别于数据集的本质：(1) passive learning → collaborative evolution（环境按 agent 实时表现动态调整，而非静态语料）；(2) single-turn Q&A → multi-turn interaction（支持多轮交互与外部工具接入）；(3) open-loop → closed-loop（agent 动作与状态变化持续耦合）。动机侧：前沿模型（GPT-5.4、Gemini-3.1-Pro、Kimi K2.5 等）的 agentic 能力已就位，但真实世界交互受成本、安全与隐私约束，环境成为可规模化产生轨迹数据、支撑 evaluation / inference-time reasoning / RL training 三类用途的基础设施。定位上，作者声明与既有 agent-centric survey（推理方法侧、系统组件协调侧）互补："organized around the lifecycle of environments, systematically covering the full pipeline of environment modeling, construction, evaluation and application"。三个 RQ：环境的关键特征与类别是什么；环境如何被系统性构建与评估；环境如何支撑 agent-environment 闭环 co-evolution。

## Method

Survey 的"方法"即其分类框架，五层结构：

**1. 形式化定义**。环境 ℰ = ⟨𝒮, 𝒜, 𝒫, ℛ, Ω, 𝒪, γ⟩ 的 POMDP 七元组；agent 为策略 π；Environment-Agent Alignment 定义为找到最大化 expected discounted return J(π) 的 π*，实现路径分 teacher 轨迹合成 + SFT（offline）与 agentic RL（PPO/GRPO/DAPO，online）两代。

**2. 八属性坐标系**（Section III）：Symbolic vs. Neural（转移动态由程序逻辑还是神经网络参数化）、Open-Loop vs. Closed-Loop、Online vs. Offline、MDP vs. POMDP、Deterministic vs. Nondeterministic、Discrete vs. Continuous、Unimodal vs. Multimodal、Single-Agent vs. Multi-Agent。

**3. 八 domain 目录**（Section IV）：GUI（Desktop/Mobile/Web：OSWorld、WindowsAgentArena、AndroidWorld、WebArena、VisualWebArena 等）、Deep Research（information search / multi-source reasoning / report writing：GAIA、BrowseComp、DeepResearchGym 等）、Embodied（navigation / manipulation / long-horizon planning：Habitat、RLBench、ALFWorld 等）、Game（open world / puzzle / social deduction / adventure / strategy：MineDojo、AvalonBench、CivRealm 等）、Tool（API-Bank、ToolBench、AppWorld、τ-bench、MCPVerse）、Code（SWE-Bench、InterCode、Terminal-Bench）、Domain-Specific、Cross-Domain。

**4. 环境合成**（Section V）分两大范式：
- **Symbolic synthesis** 三段演进：task-driven（围绕预定义任务规格构建，代表 EnvScaler——code-driven backend + SQL 数据库保证状态管理可靠）→ real-world-driven（从真实运营系统派生）→ de novo（无任务模板的全新环境生成，代表 Agent World Model、AutoEnv——AutoEnv 用 DSL 分层解耦逻辑与交互、Agent World Model 强调大规模扩展下的质量稳定；定位为扩展合成灵活性与环境空间广度的前沿）。
- **Neural synthesis** 三层表示：pixel-level（video world model 近似环境转移，代表 DreamGen）、word-level（LLM 作 learned world model 模拟状态转移，代表 WebDreamer）、latent-level（压缩表示，主打效率与抽象推理）。

**5. 环境质量评估四维**（并入 Section V）：correctness（反馈是否忠实反映预期规则，已成熟）、diversity、complexity、fidelity（对真实动态的逼近度）——后三者被明确判定 "remains under-researched"。

**6. 闭环应用**：agent 演化四路径（Section VI）——memory-centric（经验累积 + 检索，in-context 不改参数）、orchestration-centric（workflow/多组件协调优化，代表 HuggingGPT、MCPVerse）、trajectory-centric（合成环境产轨迹 → offline SFT/imitation）、exploration-centric（在线 RL：PPO/GRPO/DAPO）；环境演化三范式（Section VII）——neural-driven（调神经环境模型参数以模拟多样状态）、difficulty-driven（难度随 agent 能力课程化调节）、scaling-driven（扩场景多样性与新结构）。

## Key Results

Survey 类论文无实验，主要产出是框架与判断：

- **覆盖面**：63 页、10 图、582 条参考文献，覆盖至 2026-05；以 Figure 2 taxonomy 将八属性、八 domain 挂到三个 RQ 上。
- **核心判断 1（质量评估缺口）**：合成环境的评估四维中只有 correctness 有成熟框架，diversity/complexity/fidelity 均 under-researched——这是全文最有信息量的 gap 论断。
- **核心判断 2（co-evolution 双侧结构）**：agent 侧四路径与环境侧三范式构成互补闭环；agent-environment co-evolution theory（互适应动力学的形式化）被列为未来方向而非已有成果。
- **未来方向清单**（Section VIII）：Environment-as-a-Service（标准化、可扩展、可复现的环境部署）、multi-agent environments、neural-symbolic integration（符号可靠性 × 神经可扩展性）为三大主推；另列 dynamic long-horizon、open-ended task design、multimodal 融合、sim-to-real alignment、评估指标建设、environment scaling laws、co-evolution theory、safety & robustness、标准化与可复现性。

## Evidence Ledger

| Claim ID | Claim | Type | Source locator | Evidence excerpt | Status |
|:--|:--|:--|:--|:--|:--|
| C1 | 八对属性二分刻画环境（Symbolic/Neural…Single/Multi-Agent） | benchmark-setting | Section III / Figure 5 | "An overview of environment attributes" | source-verified |
| C2 | 八 domain：GUI/Deep Research/Embodied/Game/Tool/Code/Domain-Specific/Cross-Domain | benchmark-setting | Section IV headings | — | source-verified |
| C3 | 合成分 symbolic（task-driven/real-world-driven/de novo）与 neural（pixel/word/latent-level） | benchmark-setting | Section V | — | source-verified |
| C4 | 评估四维中 diversity/complexity/fidelity 被判 under-researched | comparison | Section V 评估小节 | "the study of evaluating diversity, complexity, and fidelity remains under-researched" | source-verified |
| C5 | agent 演化四路径：memory-/orchestration-/trajectory-/exploration-centric | benchmark-setting | Section VI | — | source-verified |
| C6 | 环境演化三范式：neural-/difficulty-/scaling-driven | benchmark-setting | Section VII | — | source-verified |
| C7 | 未来方向含 EaaS、multi-agent、neural-symbolic integration | sota-novelty | Section VIII / abstract | "standardized, scalable, and reproducible environment deployment" | source-verified |
| C8 | 代表工作归类：EnvScaler→task-driven；Agent World Model/AutoEnv→de novo synthesis（V-A3，AutoEnv 用 DSL 分层解耦）；WebDreamer→word-level；DreamGen→pixel-level | benchmark-setting | Section V-A1/V-A3, Table V/VI | 已核（原稿误将 AutoEnv/AgentWorldModel 归 task/real-world-driven） | source-verified |
| C9 | 63 页、10 图、582 条参考文献；作者属 Institute of Automation, CAS | number | arXiv comments + bib（bib1–bib582） | "63 pages, 10 figures" | source-verified |
| C10 | 三 RQ：环境特征与类别 / 系统性构建与评估 / 闭环 co-evolution | benchmark-setting | Section I-II / Figure 2 | — | source-verified |
| C11 | GUI domain 目录（IV-A）以评测 benchmark 为主；训练导向 GUI 环境合成不在 IV-A，但 V-A2（AgentSynth/TaskCraft/OSWorld-MCP/VeriEnv）有覆盖 | comparison | Section IV-A + V-A2 + Table I | 已核：组织拆分而非全文缺口 | source-verified |

## Strengths & Weaknesses

**亮点**

- **环境中心视角填了真实空位**：既有 survey 都是 agent-centric（推理方法或系统组件），把环境按 lifecycle（modeling→synthesis→evaluation→application）组织成一等对象是干净的 problem formulation，与本 vault 长期在 [[Topics/CUA-Survey]] §4 里按能力规格谈环境的取向同构。
- **质量评估 gap 的命名有价值**：明确判定 correctness 之外的 diversity/complexity/fidelity 无成熟评估框架，与本 vault 反复出现的"合成环境质量谁来验证"问题（[[Papers/2605-SEAL]] 笔记中的讨论、[[Papers/2606-CUAGym]] 的 programmatic verification 路线）互相印证——这是该 survey 对 vault 最直接的增量确认。
- **八属性是理论侧坐标系，与 CUA-Survey 六轴互补**：本 survey 的属性（可观测性、确定性、连续性、模态、agent 数）是 MDP 理论刻画；[[Topics/CUA-Survey]] §4.2.1 的六轴（Init/Reset、Verify/Reward、Parallelism、Fork/Rollback、Task Supply、Determinism/Isolation）是工程运维能力刻画。两套坐标几乎不重叠，合起来才是环境的完整规格语言——这是跨 survey 对读的主要收获。
- **四路径 × 三范式给 co-evolution 方向提供了检索骨架**：vault 中 SEAL（interface 级）、GenEnv（难度级）、AgentWorld（环境池级）可分别挂到该框架上定位（见 Notes）。

**局限**

- **与 scaffold/harness/tool 的边界未见显式处理**（基于多轮全文提取未检索到，非确证缺失）：环境定义走 POMDP 形式化 + 三 shift（vs 数据集），但 agent 侧 scaffold/harness 与环境的分界——正是 SEAL 这类 observation-wrapper 演化工作暴露的灰区——在提取中没有出现专门讨论；Tool 被处理为一个 domain 而非环境的构成组件，回避了 "tool 接口属于环境还是 harness" 的问题。
- **环境演化三范式疑似漏掉 interface/observation 级演化**：[[Papers/2605-SEAL]] 只演化训练时 observation function、不改难度不改规模不用神经环境，在 neural-/difficulty-/scaling-driven 三分里没有位置。这符合本 vault "claims not on taxonomies" 的警惕：先验分类学总有漏项，价值要看能否指导干预。
- **质量评估章停留在维度命名**：四维只有 correctness 有可操作内容，其余三维的 "under-researched" 判断本身说明该章更多是 gap 声明而非方法综述。
- **GUI domain 目录（IV-A）偏评测 benchmark**（C11，已核）：训练导向的 GUI 环境合成（AgentSynth/TaskCraft/OSWorld-MCP/VeriEnv）被归到 Section V-A2 合成章、不在 GUI domain 目录——是组织方式的拆分而非全文缺口，但也使其 domain 目录读起来更像 evaluation landscape，与 [[Topics/CUA-Survey]] §4.2 把 trainer-facing 基建（WebServ 1.78s fork、AgentGym-RL、OpenWebRL）并入 GUI 环境的取向不同。
- **co-evolution 有分类无机制**：互适应动力学、环境演化的安全性（谁验证 verifier 的演化——[[Topics/SelfEvolvingAgents-Survey]] Open Problems 已标注的完全空白）都被推到未来方向，survey 本身未提供机制分析。

## Mind Map

```mermaid
mindmap
  root((EnvEngineeringSurvey))
    Problem
      Data engineering 到 environment engineering
      三 shift 闭环 多轮 协同演化
      三 RQ 特征 构建评估 co-evolution
    Modeling
      POMDP 七元组
      八属性二分
      八 domain 目录
    Synthesis
      Symbolic 三段 task real-world de novo
      Neural 三层 pixel word latent
      质量四维 correctness diversity complexity fidelity
    Application
      Agent 四路径 memory orchestration trajectory exploration
      Environment 三范式 neural difficulty scaling
    Future
      Environment as a Service
      Multi-agent environments
      Neural-symbolic integration
