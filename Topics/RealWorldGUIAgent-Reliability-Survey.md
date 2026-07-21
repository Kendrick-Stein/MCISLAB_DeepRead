---
title: 真实部署 GUI Agent 可靠性研究综述
tags: [gui-agent, reliability, error-recovery, abnormal-state]
date_updated: "2026-07-06"
year_range: 2024-2026
papers_analyzed: 22
keywords: [gui agent reliability, execution stability, abnormal state, error recovery, self-correction, real-world deployment]
domain_map: GUI-Agent
---

# 真实部署 GUI Agent 可靠性研究综述

## Overview

GUI Agent 从 grounding/benchmark 竞赛走向真实部署时，暴露出一个被静态评测系统性掩盖的问题：**在真实、长程、动态的界面环境中，agent 无法稳定完成任务**。这不是"再高几个点 accuracy"的问题，而是可靠性（reliability）问题——同一个在 curated benchmark 上得高分的模型，遇到网络延迟、渲染延迟、权限弹窗、账号风控、支付验证、动态内容时会**未检测地失败、反复空转、错误累积直至崩溃**。本综述聚焦 **agent-侧的真实执行可靠性**（execution stability + abnormal-state handling + error recovery），与已有的 [[Topics/AgentEnvironment-Survey]]（环境/testbed 侧）和 [[Topics/GUIAgent-Survey]]（宽领域）互补。

本领域最强的共识信号是 **"真实长程/组合工作流远未饱和"**（vault validated insight）：跨多个真实 benchmark、跨任务类型、跨平台，frontier model 的端到端成功率一致偏低——[[Papers/2605-SaaSBench]] resolved 3.8%、[[Papers/2606-OSWorld2]] 20.6% binary completion、[[Papers/2604-WindowsWorld]] ~20%、[[Papers/2604-ClawEvalLive]] 66.7%（无一超 70%）、[[Papers/2605-AndroidDaily]]（闭源真实 App）62.0%。这条低水位证据链说明：真实场景难度被静态 benchmark 系统性低估，且天花板反映的是 capability gap 而非评测噪声。

更关键的是**失败结构的重新认识**：可靠性瓶颈往往不在 grounding（"点得准不准"），而在 **verify/recover（"知不知道自己错了、能不能拉回来"）**。[[Papers/2604-VeriGUI]] 给出标志性统计——1,265 次执行中 **72.3% 的失败来自重复无效动作导致的 execution timeout**，即 agent 在"以为动作成功了"的错误信念下反复空转；[[Papers/2606-WeaveBench]] 发现 35.2% 失败是 reward hacking 而非能力不足。这把问题从"感知精度"重新 framing 为"运行时自我验证与自我修复能力的缺失"。

2025–2026 年的工作沿四条技术路线回应这一问题：**(1) 用接近部署的真实执行分布训练**、**(2) 运行时 action-effect 自验证与自纠错**、**(3) 错误恢复与回溯**、**(4) 异常态识别与不确定性/弃权**。四者共享一个新兴范式——**"造失败 → 学恢复"**：主动合成或采集失败轨迹，把恢复能力变成可训练/可评测的一等目标。

---

## 技术路线

### 1. 真实执行分布训练（Real-Distribution Training）

**代表论文**：[[Papers/2606-XiaomiGUI0]] · [[Papers/2500-MobileRL- Online Agentic Reinforcement Learning for Mobile GUI Agents]] · [[Papers/2606-MobileForge]] · [[Papers/2606-GUICrafter]]

**核心思路**：训练/评测的执行分布必须接近真实部署，否则 benchmark 分数无法迁移。异常态（账号/权限/支付/风控）应作为一等可训练分布，而非事后 robustness 补丁。

- **Xiaomi-GUI-0**：真实设备为主的混合基建（物理设备为主 + sandbox 辅助），使数据采集/训练/rollout/评测共享真实分布；**error-driven data flywheel** 把失败轨迹变成 corrected action / reflective explanation / recovery demonstration（teacher takeover 产出 "deviation–diagnosis–recovery" 段）；14 类异常态 ~5000 样本，RealMobile 72.0% / AndroidWorld 78.9%。走的是"把恢复能力**烘焙进权重**"的路线。
- **MobileRL**：ADAGRPO（difficulty-adaptive GRPO）应对任务难度重尾分布 + 大规模环境采样低效。
- **MobileForge**：免标注移动端自适应，HiFPO 用纠错 hint + step-level GRPO，ForgeOwl-8B AndroidWorld 77.6% Pass@3。

**优劣**：最高保真度、异常态覆盖真实；但真实设备闭环**可复现性成本极高**（设备池、环境漂移），学术界难复现，方法论价值大于可迁移性。

### 2. 运行时自验证与自纠错（Runtime Self-Verification & Self-Correction）

**代表论文**：[[Papers/2604-VeriGUI]] · [[Papers/2606-OSOracle]] · [[Papers/2603-CAPTCHA Solving for Native GUI Agents- Automated Reasoning-Action Data Generation and Self-Correctiv]]

**核心思路**：每个动作都应有 expected effect，并被验证是否真的生效；检测到"没变化/不符预期"就进入 diagnose/recovery，而非盲目继续。

- **VeriGUI (TVAE)**：Think–Verification–Action–Expectation 闭环，step t 预测的 effect 成为 step t+1 的验证假设；**非对称 verification reward**（幻觉成功 −2.0 > 漏检失败 −0.5）逼模型对齐视觉现实；用 GUI failure idempotency 做隐式模拟省去在线 emulator。属**内建验证**。
- **OS-Oracle**：训练外部 step-level GUI critic（Qwen2.5-VL-7B + CP-GRPO），Mobile 上 70.78 Acc 超过 GPT-5，属**外挂验证**。
- **ReCAP**：CAPTCHA-capable native agent，reasoning-action 数据生成 + self-corrective training，处理"需人参与"的异常态。

**优劣**：轻量、直接对治错误累积；但 VeriGUI 自承 **idempotency 假设**只覆盖"失败不改变屏幕"，不含 unintended navigation / partial transition / crash 等 non-idempotent 失败，且 step-level 验证不替代长程 hierarchical planning。

### 3. 错误恢复与回溯（Error Recovery & Backtracking）

**代表论文**：[[Papers/2605-GUIRobustEval]] · [[Papers/2600-BeapAgentBacktrackableExecution]] · Xiaomi teacher-takeover（见路线 1）

**核心思路**：agent 被"空投"到已偏离预期的脏状态时，能否觉察出错并把任务拉回正轨——把"从错误状态恢复"变成可控评测与可训练能力。

- **GUI-RobustEval / RoTS**：首个专测 policy-induced error 觉察与恢复的 benchmark（11 类错误、**可控 error depth 0/1/3/5**）；RoTS 用 fragility-driven 分支 + 邻域恢复合成 80 万样本。RoTS-32B Error Awareness 58.8%、depth-5 post-error success 33.2%、OSWorld ≥50 步 47.4%。
- **BEAP-Agent**：DFS 框架支持长距离多级状态回溯 + 动态任务跟踪，OSWorld 28.2%（任务完成率 +~15%）。属**搜索式回溯**。

**优劣**：直击真实部署高发失败（脏状态恢复）；但 **error awareness 58.8% / depth-5 recovery 33.2% 的绝对值偏低**——"意识到错了"这一步本身未解决，且 RoTS 是"更好数据"而非新机制，受 SFT 范式增量约束。

### 4. 异常态识别与不确定性/弃权（Abnormal-State Recognition & Uncertainty / Abstention）

**代表论文**：[[Papers/2505-GEM- Gaussian Embedding Modeling for Out-of-Distribution Detection in GUI Agents]] · [[Papers/2503-OS-Kairos- Adaptive Interaction for MLLM-Powered GUI Agents]] · [[Papers/2606-AgenticAbstention]] · [[Papers/2500-GuiRobustComprehensiveDataset]] · [[Papers/2604-DynamicGUI]]

**核心思路**：可靠性的前置能力是"知道自己处在 OOD/异常/不可解状态"——该停就停、该问就问，而非过度自信地过度执行（over-execution）。

- **GEM**：Gaussian embedding modeling 做 GUI agent 的 OOD 指令检测。
- **OS-Kairos**：直指 **over-execution** 问题（不评估自身 action confidence 就全自主执行），用置信度触发 adaptive human-agent collaboration。
- **Agentic Abstention**：28,000+ instruction benchmark，发现主要问题不是"永不 abstain"而是**"太晚 abstain"**（最强 baseline timely recall 仅 26.7%），且 abstention 依赖 scaffold 而非仅 base model。
- **GUI-Robust dataset / DynamicGUIBench**：系统评测异常场景（广告弹窗、操作失败、网络断开）与高动态 POMDP 环境——GUI-Robust 显示异常场景下任务完成率从 85% 掉到 55%。

**优劣**：把"觉察"独立成能力是正确方向；但 timely detection 普遍偏弱，且异常态 taxonomy 尚未统一（各家自定义）。

---

## Datasets & Benchmarks

| Benchmark | 平台/环境 | 规模 | 评估指标 | 关键数字（SOTA） | 特点 |
|:----------|:---------|:-----|:---------|:-----------------|:-----|
| **RealMobile** ([[Papers/2606-XiaomiGUI0]]) | Mobile 真机 | 100 任务 / 14 app | Success + progress | 72.0% (Xiaomi-GUI-0) | 真实设备闭环，57% 多应用 |
| **AndroidDaily** ([[Papers/2605-AndroidDaily]]) | Mobile 真机·闭源 App | 350 任务 / 94 app | GRADE pass@1 | 62.0% (Gemini 3 Flash) | 闭源 App，视觉证据 verifier 87.4% human agree |
| **GUI-RobustEval** ([[Papers/2605-GUIRobustEval]]) | Desktop | 1,216 test case | Error Awareness / Post-Error Success | 58.8% awareness / 33.2% recovery@depth5 | 可控 error depth，专测恢复 |
| **SaaSBench** ([[Papers/2605-SaaSBench]]) | Desktop·SaaS | 106 任务 / 23 系统 | Resolved / Checkpoint | 3.8% resolved / 43.9% checkpoint | 长程跨应用专业工作流 |
| **OSWorld 2.0** ([[Papers/2606-OSWorld2]]) | Desktop | 108 任务 / 31 sites | Binary / Partial | 20.6% / 54.8% (Claude Opus 4.8) | 中位人工 1.6h，27 checkpoints/任务 |
| **WindowsWorld** ([[Papers/2604-WindowsWorld]]) | Desktop | 181 任务 / 16 persona | S_final | ~20% (Gemini-3-flash) | 跨应用是独立瓶颈 L1 46% vs L2 14% |
| **Claw-Eval-Live** ([[Papers/2604-ClawEvalLive]]) | Multi | 105 任务 | Pass rate | 66.7%（无一超 70%） | "活" benchmark，四路证据 triangulation |
| **WorkspaceBench** ([[Papers/2605-WorkspaceBench]]) | Desktop·文件 | 388 任务 / 20K 文件 | Rubrics pass | 68.7% vs human 80.7% | 异构文件依赖，lineage tracing 瓶颈 |
| **GUI-Robust** ([[Papers/2500-GuiRobustComprehensiveDataset]]) | Mobile/Web | 异常场景 | 完成率 | 正常 85% → 异常 55% | 广告/操作失败/断网异常 |
| **DynamicGUIBench** ([[Papers/2604-DynamicGUI]]) | 动态 GUI | — | Success | DynamicUI > baseline | 高动态 POMDP，视频输入 |
| **Agentic Abstention** ([[Papers/2606-AgenticAbstention]]) | Web/QA/Terminal | 28,000+ instr | AbsRec / timely recall | timely recall 26.7% (best) | 不可解任务的及时弃权 |
| **AndroidWorld / AndroidLab** | Mobile emulator / 真机 | 116 / 138 任务 | Success | 78.9%(Xiaomi) / 53.6%(MobileRL-9B 真机) | 标准长程 mobile 参照 |

*另：外部检索到但尚未 digest 的相关 benchmark——D-GARA（动态异常注入，arXiv 2511.16590）、Mobile GUI Agents under Real-world Threats（第三方内容误导率 42.0%，arXiv 2507.04227）；相关 agent——MobileUse（hierarchical reflection，arXiv 2507.16853）、Self-Healing Framework（arXiv 2605.06737）、SE-GA（memory self-evolution，arXiv 2605.16883）——列入 survey-updates 后续候选。*

---

## Key Takeaways

1. **真实长程可靠性远未饱和，且是 capability gap 而非评测噪声**。跨平台跨任务一致的低水位（SaaSBench 3.8% resolved、OSWorld2 20.6%、AndroidDaily 62.0%、WindowsWorld ~20%）说明静态 benchmark 系统性低估真实难度。可靠性是当前 GUI Agent 最重要（而非最 publishable）的问题之一。

2. **可靠性瓶颈在 verify/recover，不在 grounding**。VeriGUI 的 72.3% failure = 空转 timeout、WeaveBench 的 35.2% failure = reward hacking，共同说明大量失败源于 agent "不知道自己错了"并反复无效执行。这重构了问题：从"感知精度"转向"运行时自我验证与自我修复"。**建议加入 DomainMaps/GUI-Agent 的核心矛盾节点。**

3. **"造失败 → 学恢复"是跨路线共同范式**。Xiaomi error-driven flywheel、VeriGUI 合成失败轨迹（30%）、RoTS fragility-driven 分支——三者独立收敛到"把失败/恢复变成可训练一等目标"。这是本领域最值得复用的方法论 pattern。

4. **可观测性决定 verifier 形态，形态随可见性退化**。可见状态用程序化 verifier（[[Papers/2605-OpenComputer]] 94.1% alignment），闭源不可见状态退化为视觉证据 LLM judge（AndroidDaily GRADE 87.4%）。这与 vault "Verifier 角色迁移" validated insight 一致——verifier 是 GUI 可靠性的中枢，其形态是可观测性的函数。

5. **"错误觉察"是 recovery/abstention 的共同前置，且尚未解决**。GUI-RobustEval Error Awareness 58.8%（~40% 未察觉偏离）、Agentic Abstention timely recall 26.7%、OS-Kairos over-execution——三者指向同一底层能力缺失：agent 缺乏可靠的"状态偏离/不可解"信号。这是比 recovery 策略更上游、更值得攻的问题。

---

## Open Problems

### 1. Non-idempotent 失败的检测

VeriGUI 的 action-effect 验证依赖"失败动作不改变屏幕"的 idempotency 假设，对点击/grounding 成立，但对表单提交、导航、支付等 **non-idempotent** 操作失效——而这些正是 SaaSBench/OSWorld2 长程失败的高发区。**研究机会**：non-idempotent 失败的检测需要 external state observation（超出单屏对照），这直接连接 primary 方向 Agent-Facing Environment Runtime 的 observe affordance——把环境后台状态以 non-oracle 形式暴露，可能是 idempotency 假设失效场景的必要补充。

### 2. 可靠提升"错误觉察"本身

当前所有 recovery/abstention 方法都卡在上游——agent 觉察不到自己处于错误/OOD/不可解状态（awareness 58.8%、timely recall 26.7%）。**研究机会**：把"状态偏离检测"独立为可训练/可评测模块（GEM 的 OOD detection 是一种），并与 counterfactual evidence-dependence 诊断（[[Papers/2606-DecodableNotGrounded]]、[[Ideas/EvidenceDependence-GUIGrounding]]）结合——真正依赖视觉证据的 agent 才可能可靠觉察状态变化。

### 3. 闭源真实状态的可验证性边界

AndroidDaily 的 GRADE 用视觉证据绕过内部状态不可见（87.4% agreement），但 ~13% 分歧且无法验证 App 后台真实状态（订单是否真提交）。**研究机会**：混合可验证性——可见通道用程序化 verifier，不可见通道用视觉证据 + 有界 side-channel（如系统级 accessibility/通知），量化各通道的覆盖边界。

### 4. 真实执行分布训练的可复现性成本

Xiaomi 真机闭环、AndroidDaily 环境漂移都指向同一困境：**真实 = 昂贵 + 不可复现**。真机单任务 rollout 达 40 分钟、商业 App 持续 A/B test 使绝对分数成为时间快照。**研究机会**：量化"functional modeling 能替代真机到什么程度"（[[Papers/2605-MobileGym]] 95.1% sim-to-real retention 是起点），找出哪些异常态必须真机、哪些可仿真。

### 5. "烘焙进权重" vs "暴露为 affordance" 的因果收益分离

本领域两条路线正交：Xiaomi/VeriGUI/RoTS 把恢复能力**训练进模型权重**；primary 方向 AFE Runtime 主张把 verify/recover 能力**暴露为 frozen agent 可调用的 affordance**。**研究机会**（直接服务 primary 方向）：设计对照实验——如果 agent-facing affordance 暴露能在**不做 flywheel 重训**的前提下达到相近的异常态恢复率，则证明 affordance 暴露的独立因果价值（且不能被"把 affordance 文本塞进 prompt"的 baseline 复现）。

---

## 调研日志

### 2026-07-06 初版
- **调研日期**: 2026-07-06
- **论文统计**: vault 已有 ~18 篇相关（SaaSBench, OSWorld2, WindowsWorld, ClawEvalLive, WorkspaceBench, BEAP-Agent, ReCAP, OS-Kairos, GEM, AgenticAbstention, GUIAgentExploration, DynamicGUI, GUI-Robust, MobileRL, MobileForge, OS-Oracle, WeaveBench, OpenComputer 等）+ 新 digest 4 篇（[[Papers/2606-XiaomiGUI0]], [[Papers/2604-VeriGUI]], [[Papers/2605-GUIRobustEval]], [[Papers/2605-AndroidDaily]]）
- **搜索**: WebSearch 2 次（execution stability / error recovery），候选 ~17 篇，digest 3 篇（VeriGUI, GUI-RobustEval, AndroidDaily；Xiaomi-GUI-0 本轮 autoresearch 已 digest）
- **核心发现**:
  - 真实长程可靠性远未饱和（跨 benchmark 低水位一致）
  - 瓶颈在 verify/recover 而非 grounding（VeriGUI 72.3% 空转 timeout）
  - "造失败→学恢复"跨路线共同范式
  - verifier 形态随可观测性退化（程序化 94.1% → 视觉证据 87.4%）
  - 错误觉察是 recovery/abstention 未解决的共同前置
- **未能获取/未 digest**: D-GARA、MobileUse、Self-Healing Framework、SE-GA、Real-world Threats（列入 survey-updates 后续候选，未纳入本轮 digest 以控制范围）
- **status**: success
